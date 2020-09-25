import threading # timer delay (serene)
from transitions import Machine
from time import sleep
from datetime import datetime
import sys, os
import zmq
import socket_const

try:
    current_path    = os.path.abspath(os.path.dirname(__file__)) # /home/pi/Dev/home_alarm/ext_alarm
    base_path       = os.path.dirname(current_path)              # /home/pi/Dev/home_alarm
    sys.path.append(base_path)
    from utils.UnipiIO import UnipiInput, UnipiOutput
    from utils.config_helper import dict_from_json_file
except:
    print("Import Failed:", sys.exc_info()[0])
    raise
    
class ExtAlarm(object):
    """
    | Condition of transition -----------------------------------------------------------------
    | from \ to       | OFF               | ON        | ALERT             | WAS_ALERT         | 
    | off             | -                 | request_on| -                 | -                 | 
    | on              | request_off       | -         | detection         | -                 | 
    | alert           | request_off       | -         | -                 | timer_alert end   | 
    | was_alert       | request_off       | true      | -                 | -                 | 
    | ----------------------------------------------------------------------------------------- 
     
    | Action ---------------------------------------------------------------------------------- 
    |                 | OFF               | ON        | ALERT             | WAS_ALERT         | 
    |                 | stop serene       |           | start timer_alert | stop serene       | 
    |                 |                   |           | start serene      |                   | 
    | ----------------------------------------------------------------------------------------- 
    """
    # Define states.
    states = ['off', 'on', 'alert', 'was_alert']

    def print_state(self):
        """ Print alarm state in console for debug """
        print('out_serene:'+ str(self.out_serene.value)+\
              ' in_alert:'+ str(self.in_alert.value)+\
              ' state:'+ self.state)
              
    def __init__(self):
        self.name              = 'ExtAlarm'
        self.cycle_delay       = 0.5   # While Loop cycle delay
        self.alert_timer_delay = 3     # Delay serene ringing
        
        context = zmq.Context()
  
        # Socket SUB_COMMAND Receive Commands (start stop) from Flask (ThreadExtAlarm)
        self.SUB_COMMAND = context.socket(zmq.SUB)
        self.SUB_COMMAND.connect ("tcp://localhost:%s" % socket_const.port_socket_extalarm_command)
        self.SUB_COMMAND.setsockopt_string(zmq.SUBSCRIBE, socket_const.TOPIC_COMMAND)

        # Socket PUB_STATUS sends Status updates to Flask (ThreadExtAlarm)
        self.PUB_STATE = context.socket(zmq.PUB)
        self.PUB_STATE.bind("tcp://*:%s" % socket_const.port_socket_extalarm_state)

        # load config from json
        io_config_json = os.path.join(current_path, 'ExtAlarmConfig.json')
        
        conf = dict_from_json_file(io_config_json)
        
        # declare I/O from config
        self.in_alert   = UnipiInput(conf['in_alert'])
        self.out_serene = UnipiOutput(conf['out_serene'])
        
        self.IOs = [self.in_alert, self.out_serene]
       
        # State Machine
        self.machine = Machine(model=self, states=ExtAlarm.states, initial='off')
        self.machine.add_transition('off_to_on',          'off',      'on',        before='starting',    after='push_socket_state')
        self.machine.add_transition('any_to_off',         '*',        'off',       before='stopping',    after='push_socket_state')
        self.machine.add_transition('on_to_alert',        'on',       'alert',     before='detection',   after='push_socket_state')
        self.machine.add_transition('alert_to_was_alert', 'alert',    'was_alert', before='serene_stop', after='push_socket_state')
        self.machine.add_transition('was_alert_to_on',    'was_alert','on',        before='re_starting', after='push_socket_state')
        
    def init_timer(self):
        """ Start Serene timer, bind callback for seren stop. """
        self.timer = threading.Timer(self.alert_timer_delay, self.alert_to_was_alert)
        
    def read_inputs(self):
        """ Read physical IO from Unipi, update class variables. """
        self.in_power.read()
        self.in_alert.read()
    
    
    # --- Handle commands from web App ---
    def start_alarm(self):
        """ Command to start alarm. """
        if self.state is "off":
            self.off_to_on()
        
    def stop_alarm(self):
        """ Command to stop alarm. """
        if self.state == "alert":
            self.timer.cancel()
        self.any_to_off()
            
            
    # --- StateMachine Callbacks (Actions on state change) ---
    def starting(self):
        print('ExtMachine: start')
        self.push_socket_event('start')
    def stopping(self):
        print('ExtMachine: stop')
        self.push_socket_event('stop')
    def detection(self):
        print('ExtMachine: detection')
        self.push_socket_event('detection')
        self.init_timer()
        self.timer.start() # start timer alert
        self.out_serene.set_relay(1) # start serene
    def serene_stop(self):
        print('ExtMachine: serene_stop')
        self.push_socket_event('serene_stop')
        self.out_serene.set_relay(0) # stop serene
    def re_starting(self):
        print('restart')
        self.push_socket_event('restart')
    
    # --- Push info to web App socket ---
    def push_socket_event(self, event):
        # date = datetime.now().strftime("%d/%m/%y %H:%M:%S")
        self.PUB_STATE.send_string(socket_const.TOPIC_EVENT + " " + event)
        print("Extalarm send event "+ event)
            
    def push_socket_state(self):
        print("Extalarm send state "+ self.state)
        self.PUB_STATE.send_string(socket_const.TOPIC_STATE + " " + self.state)
    
    def run_states(self):
        """ Starting and stoping are triggered by receiving commands from web app socket """
        self.read_inputs()
        self.print_state()
        
        if self.state == "on":
            # go to state alert if PIR detection
            if (self.in_alert.value == True):
                self.on_to_alert()
        
        elif self.state == "alert":
            pass
            
        elif self.state == "was_alert":
            self.was_alert_to_on()
    
    def receive_command(self):
        """ Check if command (start, stop) received and process it
        """
        try:
            payload = self.SUB_COMMAND.recv_string(flags=zmq.NOBLOCK)
            topic, command = payload.split()
            if (topic == socket_const.TOPIC_COMMAND):
                if (command == socket_const.COMMAND_START):
                    self.start_alarm()
                    print("Extalarm receive COMMAND_START")
                elif (command == socket_const.COMMAND_STOP):
                    self.stop_alarm()
                    print("Extalarm receive COMMAND_STOP")
        # Else if no command received, do nothing
        except zmq.error.Again:
            pass 
    
    def run_states_fake(self):
        self.receive_command()
        self.push_socket_state()
        # if self.state == "on":
            # self.any_to_off()
        # elif self.state == "off":
            # self.off_to_on()
        # self.print_state()
        
            

if __name__ == '__main__':
    alarm = ExtAlarm()
    while(1):
        sleep(alarm.cycle_delay)
        alarm.run_states_fake()
