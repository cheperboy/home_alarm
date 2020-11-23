from flask import Flask, Blueprint, render_template, redirect, url_for, request, flash

from ..models import DBLog

alarms_panel = Blueprint('panel', __name__, url_prefix='/')

@alarms_panel.route('/both')
def both():
    # only by sending this page first will the client be connected to the socketio instance
    return render_template('alarms-panel.html.j2', \
                            ext_events=DBLog.commands(scope="ext", limit=5), \
                            nox_events=DBLog.commands(scope="nox", limit=5))

@alarms_panel.route('/')
#@alarms_panel.route('/panel_nox_bind')
def panel_nox_bind():
    # only by sending this page first will the client be connected to the socketio instance
    return render_template('alarms-panel-nox-bind.html.j2', \
                            logs=DBLog.log_nox_bind_ext(limit=15))
