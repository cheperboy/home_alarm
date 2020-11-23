import sys
from threading import Thread, Event
from flask_socketio import emit
from flask import Blueprint, render_template, request, current_app
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask import Flask, copy_current_request_context

from ..models import DBLog
from .. import socketio

sys.path.append("../ext_alarm")
from ext_alarm.extGateway import ThreadExtAlarmGateway


ext = Blueprint('ext', __name__, url_prefix='/ext')
thread = Thread()
thread_stop_event = Event()

@ext.route('/')
def index():
    # Called when web browser client request the page to be loaded. Then the web page will be connected and updated with connected to/with the socketio instance
    current_app.logger.info('loading page alarm/ext')
    return render_template('ext-panel.html.j2', \
                            ext_events=DBLog.commands(scope="ext", limit=5))

@socketio.on('connect', namespace='/extalarm')
def handle_connect():
    """ When a web app client connects then a gateway thread is started.
    This thread manages the interface with the Alarm Process.
    the flask app socketio instance is passed to the thread so he can send socketio messages to the web browser to update alarm status display.
    """
    # get visibility of the global thread object
    global thread
    current_app.logger.debug('New web client {} {}'.format(request.remote_addr, request.sid))

    # Start gateway thread if the thread not already running.
    if not thread.isAlive():
        current_app.logger.debug ("Starting Gateway ThreadExtAlarm")
        thread = ThreadExtAlarmGateway(socketio)
        thread.start()

    # Request status update
    thread.event_request_status = True

@socketio.on('disconnect', namespace='/extalarm')
def handle_disconnect():
    # nothing is done (thread gateway kept alive for other clients)
    # TODO Could be used to keep up to date a list of connected clients
    current_app.logger.debug('web client disconnected {} {}'.format(request.remote_addr, request.sid))

@socketio.on('command_alarm', namespace='/extalarm')
def handle_stop_alarm(json):
    """ Receive command from web socket to start / stop alarm
    Set flag to have commands processed by Alarm Process (via thread gateway)
    """
    if json['value'] == 'start_alarm':
        thread.command_alarm = True
        DBLog.new(subject="command", scope="ext", badge="primary", message=json['value'])
    elif json['value'] == 'stop_alarm':
        thread.command_alarm = False
        DBLog.new(subject="command", scope="ext", badge="success", message=json['value'])
