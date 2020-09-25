import sys
import prctl # Used to set thread name (visible in htop)
import zmq
from time import sleep
from threading import Thread, Event, current_thread
from datetime import datetime
from flask import current_app as app

from . import zmq_socket_config

context = zmq.Context()

""" Configure logger """
import logging
logger = logging.getLogger('alarm.thread')

class ThreadNoxAlarmGateway(Thread):
    """ Thread used as a "gateway" between the Flask app and the Alarm process.
    Forwards Alarm status from Alarm Process to Flask app
    Forwards commands (start/stop alarm) from Flask app to Alarm Process
    Use zmq PUB/SUB pattern to communicate with Alarm process.
    Use socketio instance (parameter given at init) to communicate with Flask app.
    Thread started when a first client connects to the web socket.
    Any new client will use the existing thread.
    Why using a thread:
    - Need a while loop to receive status continuously from Alarm Process 
    - Only one thread needed whatever how many web clients. 
    - Commands could be received directly from web server socketio handlers but 
        it is cleaner to centralize all inter-process comminication here, commands and status 
        (moreover, this thread is initialized with an instance of flask socketio allowing 
        to communicate easily with the web app).
    """
    
    def __init__(self, socketio):
        self.socketio        = socketio # Instance of socketio so that the thread interacts with web flask websoket
        self.cycle_delay     = 1        # cycle delay for execution of the thread while loop
        self.command_alarm   = None     # Flag to receive commands from websocket to thread (to alarm machine)
        
        # Flag to receive "status update" request from web app to thread (to alarm machine)
        # self.event_request_status = Event()
        self.event_request_status = None

        # Create a zmq PUB server to send message to the Alarm Process zmq client
        # using socket PUB_COMMAND to send commands start/stop to the Alarm Process
        self.PUB_COMMAND = context.socket(zmq.PUB)
        self.PUB_COMMAND.bind("tcp://*:%s" % zmq_socket_config.port_socket_noxalarm_command)        

        # Connect a zmq SUB client connected to the Alarm Process zmq server
        # using the Socket SUB_STATE to receive status/event from Alarm Process
        self.SUB_STATE = context.socket(zmq.SUB)
        self.SUB_STATE.connect ("tcp://localhost:%s" % zmq_socket_config.port_socket_noxalarm_state)
        self.SUB_STATE.setsockopt_string(zmq.SUBSCRIBE, zmq_socket_config.TOPIC_EVENT)
        self.SUB_STATE.setsockopt_string(zmq.SUBSCRIBE, zmq_socket_config.TOPIC_STATE)
        
        # Call the super class __init__ method (the suêr class is Thread)
        super(ThreadNoxAlarmGateway, self).__init__()

    def run(self):
        """ Start the Gateway thread and run infinite loop
        Forwards Alarm status from Alarm Process to Flask app
        Forwards commands (start/stop alarm) from Flask app to Alarm Process
        """
        prctl.set_name("NoxGateway")  # set thread name visible in htop
        logger.info('Init thread (delay %ss) %s' %(self.cycle_delay, str(current_thread().ident)))
        while (True):
            self.forward_command_from_web_to_alarm()
            self.forward_status_from_alarm_to_web()
            self.forward_request_status_from_web_to_alarm()

            sleep(self.cycle_delay)
                
    def forward_status_from_alarm_to_web(self):
        """ Forward to web app the status received from Alarm Process.
        Receive status using zmq SUB socket.
        Forward to web client using socketio instance.
        """
        try:
            payload = self.SUB_STATE.recv_string(flags=zmq.NOBLOCK)
            topic, message = payload.split()
            if (topic == zmq_socket_config.TOPIC_STATE):
                logger.debug('Noxalarm gateway forwading state %s' %(message))
                self.socketio.emit('noxalarmstate', {'state': message}, namespace='/noxalarm')

            elif (topic == zmq_socket_config.TOPIC_EVENT):
                logger.debug('Noxalarm gateway forwading state %s' %(message))
                date = datetime.now().strftime("%d/%m %H:%M")
                self.socketio.emit('noxalarmevent', {'alarm_event': message, 'date': date, 'user': '-'}, namespace='/noxalarm')
                
        # No command received, do nothing
        except zmq.error.Again:
            pass 
    
    def forward_command_from_web_to_alarm(self):
        """ Forward to Alarm Process the commands received from web app.
        If a command is triggered from web app, a flag is set.
        If flag is set, this function forward the command to Alarm Process, then reset flag to None.
        Command forwarded using zmq PUB socket.
        The Alarm process will call its private methods to start/stop alarm (set Unipi IO)
        """
        if self.command_alarm is not None:
            if self.command_alarm is True:
                self.command_alarm = None
                self.PUB_COMMAND.send_string(zmq_socket_config.TOPIC_REQUEST + " " + zmq_socket_config.COMMAND_START)
                logger.debug('Noxalarm gateway forwad command Start')
            if self.command_alarm is False:
                self.command_alarm = None
                self.PUB_COMMAND.send_string(zmq_socket_config.TOPIC_REQUEST + " " + zmq_socket_config.COMMAND_STOP)
                logger.debug('Noxalarm gateway forwad command Stop')
        
    def forward_request_status_from_web_to_alarm(self):
        """ Forward to Alarm Process a request to update the display.
        If a new web client connects, a flag is set.
        If flag is set, this function forward the "status update" request to Alarm Process, 
        then reset flag to None.
        The request is forwarded using zmq PUB socket.
        The Alarm process will call its private methods to send the status
        """
        # if self.event_request_status.is_set():
            # self.event_request_status.clear()
        if self.event_request_status is True:
            self.event_request_status = None
            self.PUB_COMMAND.send_string(zmq_socket_config.TOPIC_REQUEST + " " + zmq_socket_config.STATUS_UPDATE)
            logger.debug('Noxalarm gateway forward request status update')
        