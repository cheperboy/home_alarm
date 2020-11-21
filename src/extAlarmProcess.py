# coding: utf-8
from gevent import monkey
monkey.patch_all()

from os.path import abspath  as abspath  # Convert relative to absolute path
from os.path import dirname  as dirname  # Name of the last directory of a path
from os.path import basename as basename
from os.path import join     as join
from os.path import exists   as exists

# Detect ENV type from path
src_path     = abspath(dirname(__file__))           # /home/pi/Dev/home_alarm/src
project_path = dirname(src_path)                    # /home/pi/Dev/home_alarm
env_path     = dirname(project_path)                # /home/pi/Dev
conf_path    = join(env_path, "home_alarm_CONFIG/")  # /home/pi/Dev/home_alarm_CONFIG

import configparser # for debug
import signal
import sys
from os.path import join as join
from transitions import Machine
from time import sleep
from datetime import datetime
import zmq
import logging

""" Configure logger """
from utils.logger_config import flask_logger_settings
from logging.config import dictConfig
dictConfig(flask_logger_settings)
logger = logging.getLogger('extalarm.process')

""" Import project util dependencies """
from utils.UnipiIO       import UnipiInput, UnipiOutput
from utils.config_helper import dict_from_json_file
from utils.emails        import EmailAlarmAlert
from utils.sms           import SmsAlarmAlert
from utils.util_timer    import Countdown
from web                 import create_app
from web.models          import DBLog

""" import socket to thread gateway """
from ext_alarm import zmq_socket_config

""" UniPi IO config file """
UNIPI_IO_CONFIG = join(conf_path, 'software', 'nox_unipi_io.json')

#DEBUG = None
DEBUG = True

BIND_TO_NOX = True # None / True. bind start/stop to NoxAlarm status

class ExtAlarm(object):
  """ La class ExtAlarm est une machine à état qui vérifie l'état dedes détecteurs.
  L'initialisation configure 
  - les entrées (PIR Terrasse) 
  - les sortie (Lumière Terrasse)
  L'appel de la fonction run_states() provoque le rafraississement des valeurs en entrées. 
  run_states() doit être appelée dans une boucle while à interval régulier (~1 seconde)
  Lorsque la machine change d'état, la fonction push_socket_event() émet l'info sur un socket. 
  le socket est passé en paramètre à l'init.
  Un programme externe (appli web) appelle la fonction push_socket_state() à intervalle régulier 
  pour connaitre l'état de la machine (on, off, etc).
  """
  
  states = ['init' , 'off'     , 'waiton'  , 'on' , 'alert'     ]
  
  colors = ['info' , 'success' , 'primary' , 'primary'          , 'warning'   , 'primary'    ]
  events = ['init' , 'stop'    , 'start'   , 'start_delayout'   , 'detection' , 'serene_stop']
  
  DELAY_ALERT = 60*4 # Delay for alert timer (in ~second)
  DELAY_FLASH_GARAGE = 60*4 # Delay for alert timer (in ~second)

  name        = 'Ext'
  cycle_delay = 1    # While Loop cycle delay
  state_requested    = None # Record the state On/Off requested by user
  timer_waitout      = Countdown("wait_out", 2)
  timer_light_garage = Countdown("light_garage", 10)
  timer_alert        = Countdown("alert", 10)


  # --- Init functions ---
  def init_socket(self):
    context = zmq.Context()
    
    try:
      # Socket SUB_COMMAND Receive Commands (start stop) from Flask (ThreadExtAlarm)
      self.SUB_COMMAND = context.socket(zmq.SUB)
      self.SUB_COMMAND.connect ("tcp://localhost:%s" % zmq_socket_config.port_socket_extalarm_command)
      self.SUB_COMMAND.setsockopt_string(zmq.SUBSCRIBE, zmq_socket_config.TOPIC_REQUEST)

      # Socket PUB_STATUS sends Status updates to Flask (ThreadExttAlarm)
      self.PUB_STATE = context.socket(zmq.PUB)
      self.PUB_STATE.bind("tcp://*:%s" % zmq_socket_config.port_socket_extalarm_state)
    except:
      msg = 'Failed init ZMQ socket'
      logger.exception(msg)
      self.exit(msg, exit_now=True)
      
  def init_config(self):
    try:
      # load config from json
      logger.info("Loading config file %s" % (UNIPI_IO_CONFIG))
      conf = dict_from_json_file(UNIPI_IO_CONFIG)
      # declare I/O from config
      self.in_nox_alert       = UnipiInput(conf['in_alert'])
      self.in_nox_power       = UnipiInput(conf['in_power'])
      self.in_pir_terrasse    = UnipiInput(conf['in_pir_terrasse'])
      self.in_pir_garage      = UnipiInput(conf['in_pir_garage'])
      self.out_light_terrasse = UnipiOutput(conf['out_light_terrasse'])
      self.out_light_garage   = UnipiOutput(conf['out_light_garage'])
    except Exception as e:
      name = e.__class__.__name__ # name of the exception eg
      if (name == 'FileNotFoundError'):
        logger.error('Config file not found %s' % (UNIPI_IO_CONFIG))
      elif (name == 'KeyError'):
        logger.error('config file corrupted')
      else:
        # Generic error: log trace
        logger.exception('Error loading config %s' % (str(sys.exc_info()[0])))
      
      # Whatever the exception, conf failed, exit the program
      msg = 'Failed init Config'
      self.exit(msg, exit_now=True)
  
  def init_statemachine(self):
    # State Machine
    self.machine = Machine(model=self, states=ExtAlarm.states, initial='init')
    
    # Transitions
    self.machine.add_transition('off_to_waiton',  'off',     'waiton',    before='start_delayout',after='push_socket_state')
    self.machine.add_transition('waiton_to_on',   'waiton',  'on',        before='starting',      after='push_socket_state')
    self.machine.add_transition('any_to_off' ,    '*'  ,     'off',       before='stopping',      after='push_socket_state')
    self.machine.add_transition('on_to_alert',    'on' ,     'alert',     before='detection',     after='push_socket_state')
    self.machine.add_transition('alert_to_on',    'alert',   'on',        before='serene_stop',   after='push_socket_state')
    #self.machine.add_transition('was_alert_yo_on',    'was_alert','on',       before='serene_stop', after='push_socket_state')
  
  def init_state(self):
    """ Set the real state of the system when the program (re)start
    Transition init -> any is done 
    callback leave_init() is call manually.
    No email/sms alert will be sent.
    If Nox alarm is ON, then ExtAlarm is started.
    If Nox alarm is ON and under alert, then ExtAlarm is put on alert.
    """
    self.out_light_terrasse.set_relay(0)
    self.out_light_garage.set_relay(0)
    self.read_inputs()
    if (self.in_pir_terrasse.value == 1) and (self.in_nox_power.value == 1):
      self.state = 'alert'
    elif (self.in_nox_power.value == 1):
      self.state = 'waiton'
    else:
      self.state = 'off'
    self.leave_init()
    
  def __init__(self):
    logger.info('Starting ...')
    
    self.run = True # Flag to stop while loop. (on KeyboardInterrupt or SIGINT)
  
    # Register signal handler
    # KeyboardInterrupt (SIGINT) managed directly in main loop
    signal.signal(signal.SIGTERM, self.exit_from_signals) # Supervisor Exit code (15)
    
    self.init_socket()
    self.init_config()
    self.init_statemachine()
    self.init_state() # Read inputs and Set state after init
        
  def __str__(self):
    out = ''
    out += ('Ext: %s | ' % (self.state))        
    for input in [self.in_pir_terrasse, self.in_pir_garage]:
      out += ('%s %s | ' % (input.name, input.value))        
    for output in [self.out_light_terrasse, self.out_light_garage]:
      out += ('%s %s | ' % (output.name, output.value))        
    out += "wait_out %s " % str(self.timer_waitout)
    out += "alert %s " % str(self.timer_alert)
    out += "garage %s " % str(self.timer_light_garage)
    # out += ('timer alert %s | ' % (self.timer_alert))        
    # out += ('timer light garage %s | ' % (self.timer_light_garage))        
    return(out)
    
  # --- Exit functions (Stop Process) ---
  def exit_from_signals(self, signal_num, frame):
    """ Callback called when SIGTERM received from supervisor 
    Do call exit() with detail of the signal_num
    """
    detail = 'signal {}'.format(signal_num)
    self.exit(detail)

  def exit(self, detail, exit_now=None):
    """ Stop the process (log before)
    'exit_now': Option to stop now or to set self.run to False (will stop at the end of the current while loop cycle)
    """
    self.make_DBLog('system', 'exit', 'danger', detail=detail)
    logger.critical('Exit caused by {}'.format(detail))
    msg = 'exit'
    if exit_now: sys.exit() # exit here
    else: self.run = False  # exit after end of current loop


  # --- Handle commands from web App ---
  def start_alarm(self):
    """ Command to start alarm. """
    self.state_requested = 1
    
  def stop_alarm(self):
    """ Command to stop alarm. """
    self.state_requested = 0

    
  # --- StateMachine Callbacks (Actions on state change) ---
  def leave_init(self):
    """ From state init to any other state
    This is not a callback (called manually)
    """
    msg = 'init (state: {})'.format(self.state)
    logger.info(msg)
    event = 'init'
    self.push_socket_event(event)        
    color = ExtAlarm.colors[ExtAlarm.events.index(event)]
    self.make_DBLog('system', msg, color)

  def start_delayout(self):
    self.timer_waitout.start()
    event = 'start_delayout'
    logger.info('event %s' % (event))
    self.push_socket_event(event)
    color = ExtAlarm.colors[ExtAlarm.events.index(event)]
    self.make_DBLog("event", event, color)

  def starting(self):
    self.timer_waitout.stop()
    event = 'start'
    logger.info('event %s' % (event))
    self.push_socket_event(event)
    color = ExtAlarm.colors[ExtAlarm.events.index(event)]
    self.make_DBLog("event", event, color)

  def stopping(self):
    self.stop_light_garage()
    self.stop_light_alert()
    self.timer_waitout.stop()
    event = 'stop'
    logger.info('event %s' % (event))
    self.push_socket_event(event)
    color = ExtAlarm.colors[ExtAlarm.events.index(event)]
    self.make_DBLog("event", event, color)

  def detection(self):
    self.start_light_garage()
    self.start_light_alert()
    event = 'detection'
    logger.info('event %s' % (event))
    self.push_socket_event(event)
    color = ExtAlarm.colors[ExtAlarm.events.index(event)]
    self.make_DBLog("event", event, color)
    self.make_alert("Alert", ExtAlarm.name, event)

  def serene_stop(self):
    self.stop_light_garage()
    self.stop_light_alert()
    event = 'serene_stop'
    logger.info('event %s' % (event))
    self.push_socket_event(event)
    color = ExtAlarm.colors[ExtAlarm.events.index(event)]
    self.make_DBLog("event", event, color)
    self.make_alert("Info", ExtAlarm.name, event)
        
  @staticmethod
  def make_alert(*args):
    """ wrapper method to call mail & sms alerts """
    if not DEBUG:
      try: SmsAlarmAlert(*args)
      except: logger.exception('Fail calling SmsAlarmAlert()')
      try: EmailAlarmAlert(*args)
      except: logger.exception('Fail calling EmailAlarmAlert()')
  
  @staticmethod
  def make_DBLog(subject, event, badge, detail=''):
    """ wrapper method to call DBLog.new() on alarm event """
    app = create_app()
    with app.app_context():
      DBLog.new(subject=subject, scope="ext", badge=badge, message=event, ip='-', user='-', detail=detail)

  # --- Push info to web App socket ---
  def push_socket_event(self, event):
    self.PUB_STATE.send_string(zmq_socket_config.TOPIC_EVENT + " " + event)
    logger.debug("Extalarm send event "+ event)
      
  def push_socket_state(self):
    if DEBUG: logger.debug("Extalarm send state "+ self.state)
    self.PUB_STATE.send_string(zmq_socket_config.TOPIC_STATE + " " + self.state)

  # --- Read UniPi inputs ---
  def read_inputs(self):
    """ Read physical IO from Unipi, update class variables. """
    self.in_nox_alert.read()
    self.in_nox_power.read()
    self.in_pir_terrasse.read()
    self.in_pir_garage.read()
    self.out_light_terrasse.read()
    self.out_light_garage.read()

  def read_inputs_debug(self):
    """ Read physical IO from Unipi, update class variables. """
    # Detect ENV type from path
    DIR          = abspath(dirname(__file__))           # /home/pi/Dev/home_alarm/src
    CONFIG_FILE  = join(DIR, "extAlarmProcess_debug.ini")
    # Load config file
    if not exists(CONFIG_FILE):
      print("Exit. Config file not found " + CONFIG_FILE)
      exit()
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    # declare I/O from config
    self.in_nox_alert.value    = int(config['inputs']['in_nox_alert'])
    self.in_nox_power.value    = int(config['inputs']['in_nox_power'])
    self.in_pir_terrasse.value = int(config['inputs']['in_pir_terrasse'])
    self.in_pir_garage.value   = int(config['inputs']['in_pir_garage'])
    
  def start_light_garage(self):
    """ If nox is ON and pir_garage is 1, then set light garage to ON and start timer"""
    self.out_light_garage.set_relay(1)
    self.timer_light_garage.start()
  def stop_light_garage(self):
    """ If nox is ON and pir_garage is 1, then set light garage to ON and start timer"""
    self.out_light_garage.set_relay(0)
    self.timer_light_garage.stop()
  
  def start_light_alert(self):
    """ set alert light and serene to ON and start timer"""
    self.out_light_terrasse.set_relay(1)
    self.timer_alert.start()
  def stop_light_alert(self):
    """ set alert light and serene to OFF and stop timer"""
    self.out_light_terrasse.set_relay(0)
    self.timer_alert.stop()
  
  def run_states(self):
    """ Process transitions considering UniPi inputs 
    """
    if (self.state == "off"):
      self.stop_light_garage()
      if ((BIND_TO_NOX and (self.in_nox_power.value == 1)) or (self.state_requested == 1)):
        self.off_to_waiton()
    
    elif (self.state == "waiton"):
      if ((BIND_TO_NOX and (self.in_nox_power.value == 0)) or (self.state_requested == 0)):
        self.any_to_off()
      
      elif self.timer_waitout.has_expired():
        self.waiton_to_on()
      
    elif self.state == "on":
      if ((BIND_TO_NOX and (self.in_nox_power.value == 0)) or (self.state_requested == 0)):
        self.any_to_off()
        
      elif ((self.in_pir_terrasse.value == 1) or (self.in_nox_alert.value == 1)):
        self.on_to_alert()

      # special management of garage light
      if (self.in_pir_garage.value == 1):
        self.start_light_garage()
      if (self.timer_light_garage.has_expired()):    
        self.stop_light_garage()
    
    elif self.state == "alert":
      if ((BIND_TO_NOX and (self.in_nox_power.value == 0)) or (self.state_requested == 0)):
        self.any_to_off()
      
      elif (self.in_pir_terrasse.value == 1):
        self.timer_alert.start()
      
      elif (self.timer_alert.has_expired()):
        self.timer_alert.stop()
        self.alert_to_on()


  def receive_request(self):
    """ Check if a request is received and process it
    Request can be Command (start, stop) 
    Request can be "Status update" requested by web app 
    """
    try:
      payload = self.SUB_COMMAND.recv_string(flags=zmq.NOBLOCK)
      topic, command = payload.split()
      if (topic == zmq_socket_config.TOPIC_REQUEST):
        if (command == zmq_socket_config.COMMAND_START):
          logger.debug("Extalarm receive COMMAND_START")
          self.start_alarm()
        elif (command == zmq_socket_config.COMMAND_STOP):
          logger.debug("Extalarm receive COMMAND_STOP")
          self.stop_alarm()
        elif (command == zmq_socket_config.STATUS_UPDATE):
          logger.debug("Extalarm receive REQUEST_STATUS_UPDATE")
          self.push_socket_state()
    
    # Else if no command received, do nothing
    except zmq.error.Again:
      pass 

      
if __name__ == '__main__':
  """ Init ext Alarm Statemachine and run infinite loop
  Called from console for debug
  Called and managed by supervisor for production
  """
  if DEBUG: logger.warning("DEBUG mode ON")

  ext = ExtAlarm()
  logger.info("Process is Running (cycle delay %ss)" % (ext.cycle_delay))
  
  while(ext.run):
    try:
      if DEBUG: logger.debug('{}'.format(ext))
      if DEBUG:
        ext.read_inputs_debug()
      else:
        ext.read_inputs()
      ext.run_states()
      if not DEBUG:
        ext.receive_request()
      # Commented out : no more sent each second but on demand (when web page is loaded or on alarm state change)
      # ext.push_socket_state()
      sleep(ExtAlarm.cycle_delay)
    except KeyboardInterrupt:
      logger.warning("Exit caused by KeyboardInterrupt")
      ext.exit('KeyboardInterrupt', exit_now=False)
    