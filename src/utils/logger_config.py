from os.path import abspath  as abspath  # Convert relative to absolute path
from os.path import dirname  as dirname  # Name of the last directory of a path
from os.path import basename as basename
from os.path import join     as join

import colorlog

module_path  = abspath(dirname(__file__))             # /home/pi/Dev/home_alarm/src/etc
src_path     = dirname(module_path)                   # /home/pi/Dev/home_alarm/src
project_path = dirname(src_path)                      # /home/pi/Dev/home_alarm
project_name = basename(project_path)                 # home_alarm
env_path     = dirname(project_path)                  # /home/pi/Dev
log_path     = join(env_path, project_name + '_LOG/') # /home/pi/Dev/home_alarm_LOG

log_colors = {
    'DEBUG':    'cyan',
    'INFO':     'green',
    'WARNING':  'yellow',
    'ERROR':    'red',
    'CRITICAL': 'red,bg_white'
}

datefmt     = '%Y-%m-%d %H:%M:%S'
formatters  = {
    'full':
        {
        '()': 'colorlog.ColoredFormatter',
        'log_colors': log_colors,
        'format': '%(log_color)s%(asctime)s | %(levelname)-8s | %(name)s | %(module)s | %(message)s | [%(pathname)s:%(lineno)d]',
         'datefmt': datefmt
        },

    'standard':
        {
        '()': 'colorlog.ColoredFormatter',
        'log_colors': log_colors,
        'format': '%(log_color)s%(asctime)s | %(levelname)-8s | %(name)s | %(module)s | %(message)s',
        'datefmt': datefmt
        },

    'console': {
        '()': 'colorlog.ColoredFormatter',
        'log_colors': log_colors,
        'format':
            "%(log_color)s%(levelname)-8s | %(name)s | %(module)s | %(funcName)s | %(message)s",
    }
}

flask_logger_settings = {
    'version': 1,
    'formatters': formatters,
    'handlers': {
        # console handler
        'stdout': {
            'class': 'logging.StreamHandler',
            # 'stream': 'ext://flask.logging.wsgi_errors_stream',
            'stream': 'ext://sys.stdout',
            'formatter': 'console'
        },
        # default file handler
        'file_info': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': join(log_path, 'flask_app.log'),
            'maxBytes': 5000000,
            'backupCount': 2
        },
        # default file for errors
        'file_err': {
            'level': 'WARNING',
            'formatter': 'full',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': join(log_path, 'flask_app.err'),
            'maxBytes': 5000000,
            'backupCount': 2
        },
        # file for failed request
        'file_request_fail': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': join(log_path, 'request_fail.log'),
            'maxBytes': 5000000,
            'backupCount': 1
        },
        # file for specific debug
        'file_debug': {
            'level': 'DEBUG',
            'formatter': 'full',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': join(log_path, 'debug.log'),
            'maxBytes': 5000000,
            'backupCount': 10
        },
    },

    'loggers': {
        # To see the logs of an extension, add its logger name here with a level filter
        # or put a higher level to the root logger which catch every logs
        # Exemple of a logger:
        # 'foo': {                    # All logger named "foo.bar" are childs and will be catched
            # 'level': 'DEBUG',
            # 'handlers': ['stdout'],
            # 'propagate': False      # this logger is catched here, then don't duplicate its messages to root logger
        # },
        'gunicorn.error': {
            'level': 'DEBUG',
            'handlers': ['stdout', 'file_info', 'file_err'],
            'propagate': False   # don't duplicate to root logger
        },
        'werkzeug': {
            'level': 'WARNING',
            'propagate': False   # don't duplicate to root logger
        },
        'flask.app.req': {       # dedicated for failed requests
            'level': 'DEBUG',
            'handlers': ['stdout', 'file_request_fail'],
            'propagate': False   # don't duplicate to root logger
        },
        'flask.app': {
            'level': 'DEBUG',
            'handlers': ['stdout', 'file_info', 'file_err'],
            'propagate': False   # don't duplicate to root logger
        },

        # logger 'alarm' will gather all children of the kind 'alarm.thread' and 'alarm.process'
        'alarm': {
            'level': 'WARNING',
            # 'level': 'DEBUG',
            'handlers': ['stdout', 'file_info', 'file_err'],
            'propagate': False   # don't duplicate to root logger
        },
        'extalarm': {
            'level': 'DEBUG',
            'handlers': ['stdout', 'file_info', 'file_err'],
            'propagate': False   # don't duplicate to root logger
        },
        'engineio': {
            'level': 'DEBUG',
            'handlers': ['stdout', 'file_debug'],
            'propagate': True
        },
    },
    # Declare root logger to catch all other loggers not declared above (all extensions, urllib, transitions, ..)
    # level set to WARNING lots of useless messages (catch only what is important).
    # level could be raised to info or debug when debugging a specific issue.
    'root': {
        'level': 'WARNING',     # don't log Debug message of extensions (urlib, ...)
        'handlers': ['stdout', 'file_info', 'file_err']
    },
    'disable_existing_loggers': False
}
