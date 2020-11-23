from flask import Blueprint, session, redirect, url_for, render_template, request
from flask_login import login_required

from ..models import User, DBLog
from .. import db
from .system_info import *

admin = Blueprint('admin', __name__)

# pages_categories    = ["alarm", "system"]
pages_alarm         = ["logs", "logins", "commands", "events", "system"]

@admin.route('/')
@login_required
def index():
    return redirect(url_for('admin.logs'))

@admin.route('/logins')
@login_required
def logins():
    user_logs   = DBLog.logins()
    return render_template('admin/partials_alarm/_logins.html.j2', \
                            current_page="logins", \
                            pages_alarm=pages_alarm, \
                            user_logs=user_logs)

@admin.route('/commands')
@login_required
def commands():
    command_logs = DBLog.commands()
    return render_template('admin/partials_alarm/_commands.html.j2', \
                            current_page="commands", \
                            pages_alarm=pages_alarm, \
                            logs=command_logs)

@admin.route('/events')
@login_required
def events():
    event_logs = DBLog.events()
    return render_template('admin/partials_alarm/_commands.html.j2', \
                            current_page="events", \
                            pages_alarm=pages_alarm, \
                            logs=event_logs)

@admin.route('/logs')
@login_required
def logs():
    """ Display All logs """
    logs   = DBLog.all()
    return render_template('admin/partials_alarm/_logs.html.j2', \
                            current_page="logs", \
                            pages_alarm=pages_alarm, \
                            logs=logs)

@admin.route('/system')
@login_required
def system():
    """ Display All logs """
    """Display System Info"""
    params = {}
    params["network"] = {
        'ip lan eth'    : ip_lan_eth(),
        'ip lan wifi'   : ip_lan_wifi(),
        'hostname'      : hostname()
    }
    params["system"] = {
        'date'          : system_date(),
        'uptime'        : system_uptime(),
        'cpu_temp'      : cpu_temp()
    }
    params["Nexmo (SMS)"] = {
        'Balance'       : nexmo_balance()
    }
    params["disk_space"] = disk_space()
    params["supervisor"] = supervisor_status()
    params["service"] = {
        'nginx'       : service_nginx_status(),
        'supervisor'  : service_supervisor_status(),
        'evok'        : service_evok_status()
    }
    params["db_size"]    = db_size()
    params["log_size"]   = log_size()

    return render_template('admin/partials_alarm/_system.html.j2', \
                            current_page="system", \
                            pages_alarm=pages_alarm, \
                            params = params)
