import sys
from threading import Thread, Event
from flask_socketio import emit
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask import Flask, render_template, url_for, copy_current_request_context

from ..models import DBLog
from .. import socketio

sys.path.append("../ext_alarm")
from ext_alarm.thread import ThreadExtAlarm

ext = Blueprint('ext', __name__, url_prefix='/ext')
thread = Thread()
thread_stop_event = Event()

@ext.route('/')
def index():
    # Called when web browser client request the page to be loaded. Then the web page will be connected and updated with connected to/with the socketio instance
    return render_template('ext-panel.html.j2', \
                            ext_events=DBLog.commands(scope="ext", limit=5))

@socketio.on('connect', namespace='/extalarm')
def handle_connect():
    """ When a web app client connects then a gateway thread is started.
    This thread manages the interface with the Alarm Process.
    the flask app socketio instance is passed to the thread so he can send socketio messages to the web browser to update alarm status display.
    """
    global thread # get visibility of the global thread object
    print('New client connected on extalarm')
    # Start gateway thread if the thread not already running.
    if not thread.isAlive():
        print ("Starting Gateway ThreadExtAlarm")
        thread = ThreadExtAlarm(socketio)
        thread.start()

@socketio.on('disconnect', namespace='/extalarm')
def handle_disconnect():
    # nothing is done (thread gateway kept alive for other clients)
    # TODO Could be used to keep up to date a list of connected clients
    print('Web client disconnected')

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
