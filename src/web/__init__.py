from gevent import monkey
monkey.patch_all()
# import eventlet
# eventlet.monkey_patch()
import colors

import json
from random import random
from time import sleep
from threading import Thread, Event

from flask import Flask, render_template, url_for, copy_current_request_context, request
from flask_login import LoginManager

from flask_socketio import SocketIO
socketio = SocketIO()

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect()

from flask_talisman import Talisman

# from flask_mail import Mail
# mail = Mail()

def config_from_secret(app):
    """ Update config from secret file
        secret file path is defined in app.config['SECRET_CONF']
        Example of alarm_secret_config.json
        {
            "common" : {
                "MAIL_PASSWORD"    : "gmail_app_password",
                "ADMIN_EMAILS"     : ["admin@gmail.com"],
                "SECRET_KEY"       : "secret_key",
                "NEXMO_API_KEY"    : "xxx",
                "NEXMO_API_SECRET" : "xxx"
            },
            "production" : {
                "URL" : "http://foo.hd.free.fr:",
                "USERS_EMAILS"     : ["user_prod@gmail.com"],
                "USERS_PHONES"     : ["33600000000"]
            },
            "development" : {
                "USERS_EMAILS"     : ["user_test@gmail.com"],
                "USERS_PHONES"     : ["33600000000"]
            }
        }
    """
    try:
        secret_conf_file = app.config['SECRET_CONF']
        with open(secret_conf_file) as f:
            json_config = json.load(f)
        for conf in ['common', app.config['ENV']]:
            app.config.update(json_config[conf])
    except IOError as e:
        err = 'IOError loading conf file (file not existing?): ' + secret_conf_file + str(e)
        app.logger.error(err)
    except ValueError as e:
        err = 'ValueError loading JSON : ' + secret_conf_file + ' ' + str(e)
        app.logger.error(err)

def register_callbacks(app):
    @app.after_request
    def after_request(response):
        """ Logging after every request. """

        # ad = colors.color("toto", fg='red')

        if request.path == '/favicon.ico':
            return response
        elif request.path.startswith('/static'):
            return response
        # This avoids the duplication of registry in the log,
        # since that 500 is already logged via @app.errorhandler.
        # if response.status_code != 500:
        if (app.config['ENVNAME'] == 'Dev'):
            remote_ip = request.remote_addr # LAN ip
        else:
            remote_ip = request.headers.get('X-Real-IP', '') # WAN ip
        host    = request.host
        method  = request.method
        path    = request.path
        # url = request.url
        status  = response.status_code
        str_request = f'{host}{path}'
        log = f'{status} {method} Request from {remote_ip} to {str_request}'
        if response.status_code == 200:
            app.logger.info(log)
        else:
            # Specific child logger for wrong requests
            app.logreq.info(log)
        return response

def register_blueprints(app):
    app.logger.debug("PANEL_NOX {}".format(app.config['PANEL_NOX']))
    app.logger.debug("PANEL_EXT {}".format(app.config['PANEL_EXT']))
    from .views.alarms_panel import alarms_panel as panel_bp
    from .views.nox import nox as nox_bp
    from .views.login import login as login_bp
    from .views.admin import admin as admin_bp
    app.register_blueprint(panel_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")    
    app.register_blueprint(nox_bp)
    if app.config['PANEL_EXT']:
        from .views.ext import ext as ext_bp
        app.register_blueprint(ext_bp)

def configure_talisman(app):
    allow_all = {
        'default-src': [
            '\'self\'',
            '*',
            '\'unsafe-inline\''
        ],
    }

    csp = {
    'img-src': [
       '\'self\'',
       'data:'    # bootstrap navbar img 
    ],
    'default-src': [
       '\'self\'',
       # '*',
       '*.fontawesome.com',
       '*.w3.org/',
       'cdnjs.cloudflare.com',
       'code.jquery.com',
       'stackpath.bootstrapcdn.com',
    ],
    'font-src': [
       '\'self\'',
       '*.fontawesome.com',
    ],
    'script-src': [
        '\'self\'', 
        'cdnjs.cloudflare.com',
        'code.jquery.com',
        'stackpath.bootstrapcdn.com',
        'cdn.jsdelivr.net',
        '*.fontawesome.com',
        ],
    'style-src': [
        '\'self\'', 
        'stackpath.bootstrapcdn.com',
        '*.fontawesome.com',
    ]
    }
    talisman = Talisman(
        app,
        content_security_policy=csp,
        # content_security_policy=allow_all,
        content_security_policy_nonce_in=['script-src', 'style-src']
    )

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    
    # Talisman(app) # Security stuffs
    configure_talisman(app)

    app.jinja_env.line_statement_prefix = '#'

    config_from_secret(app)

    # Configure logger
    from utils.logger_config import flask_logger_settings
    from logging.config import dictConfig
    dictConfig(flask_logger_settings)

    # Specific child logger for wrong requests
    import logging
    app.logreq = logging.getLogger('flask.app.req')

    register_blueprints(app)
    register_callbacks(app)

    db.init_app(app)
    csrf.init_app(app)
    # mail.init_app(app)

    # login manager
    login_manager = LoginManager()
    login_manager.login_view = 'login.index'
    login_manager.init_app(app)
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    # socketio.init_app(app, async_mode='eventlet')
    socketio.init_app(app, async_mode='gevent')
    # socketio.init_app(app, async_mode='gevent', logger=False, engineio_logger=False, log_output=False)

    return (app)
