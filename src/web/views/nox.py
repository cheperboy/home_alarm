import sys
from threading import Thread, Event
from flask import Blueprint, render_template, request, current_app

from ..models import DBLog
from .. import socketio

sys.path.append("../nox_alarm")
from nox_alarm.noxGateway import ThreadNoxAlarmGateway

nox = Blueprint('nox', __name__, url_prefix='/nox')
thread = Thread()
thread_stop_event = Event()
# clients = []

@nox.route('/')
def index():
    """Called when web browser client request the page to be loaded.
    Then the web page will be connected and updated with connected
    to/with the socketio instance
    """
    current_app.logger.info('loading page alarm/nox')
    return render_template('nox-panel.html.j2', \
                            nox_events=DBLog.all(scope  = "nox",
                                                 subject= ["event", 'system'], \
                                                 limit  = 7 ))

@socketio.on('connect', namespace='/noxalarm')
def handle_connect():
    """ When a web app client connects then a gateway thread is started.
    This thread manages the interface with the Alarm Process.
    the flask app socketio instance is passed to the thread so he
    can send socketio messages to the web browser to update alarm status display.
    """
    # get visibility of the global thread object
    global thread
    current_app.logger.debug('New web client {} {}'.format(request.remote_addr, request.sid))
    # Start gateway thread if the thread not already running.
    if not thread.isAlive():
        current_app.logger.debug("Starting Thread Gateway")
        thread = ThreadNoxAlarmGateway(socketio)
        thread.start()

    # current_app.logger.debug('Web client requesting status update')
    # thread.event_request_status.set()
    thread.event_request_status = True
    # global clients
    # clients.append()

@socketio.on('disconnect', namespace='/noxalarm')
def handle_disconnect():
    # nothing is done (thread gateway kept alive for other clients)
    # TODO Could be used to keep up to date a list of connected clients
    current_app.logger.debug('web client disconnected {} {}'.format(request.remote_addr, request.sid))

@socketio.on('command_alarm', namespace='/noxalarm')
def handle_command_alarm(json):
    """ Receive command from web socket to start / stop alarm
    """
    current_app.logger.info("client command %s" % (json['value']))
    if json['value'] == 'start_alarm':
        thread.command_alarm = True
        DBLog.new(subject="command", scope="nox", badge="primary", message=json['value'])
    elif json['value'] == 'stop_alarm':
        thread.command_alarm = False
        DBLog.new(subject="command", scope="nox", badge="success", message=json['value'])
