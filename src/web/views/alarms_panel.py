from flask import Flask, Blueprint, render_template, redirect, url_for, request, flash

from ..models import DBLog

alarms_panel = Blueprint('panel', __name__, url_prefix='/')

@alarms_panel.route('/')
def index():
    # only by sending this page first will the client be connected to the socketio instance
    return render_template('alarms-panel.html.j2', \
                            ext_events=DBLog.commands(scope="ext", limit=5), \
                            nox_events=DBLog.commands(scope="nox", limit=5))
