""" Flask App configuration."""
from os.path import abspath  as abspath  # Convert relative to absolute path
from os.path import dirname  as dirname  # Name of the last directory of a path
from os.path import basename as basename
from os.path import join     as join
import json

# Detect ENV type from path
src_path         = abspath(dirname(__file__)) # /home/pi/Dev/home_alarm/src
project_path     = dirname(src_path)          # /home/pi/Dev/home_alarm
env_path         = dirname(project_path)      # /home/pi/Dev
ENVNAME          = basename(env_path)         # Dev

project_name = basename(project_path)                            # home_alarm
DB_PATH      = join(env_path, project_name + '_DB/')             # /home/pi/Dev/home_alarm_DB
LOG_PATH     = join(env_path, project_name + '_LOG/')            # /home/pi/Dev/home_alarm_LOG
conf_path    = join(env_path, project_name + '_CONFIG/')         # /home/pi/Dev/home_alarm_CONFIG

# /home/pi/Dev/home_alarm_CONFIG/software/flask_config_secret.json
SECRET_CONF  = join(conf_path, 'software/', 'flask_config_secret.json') 

""" Host """
HOST = '0.0.0.0'
PORT = 5000

SQLALCHEMY_TRACK_MODIFICATIONS  = False
DEBUG_TB_INTERCEPT_REDIRECTS    = False # Debug toolbar option
WTF_CSRF_ENABLED                = True

SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(join(DB_PATH, 'app.db'))
SQLALCHEMY_BINDS = {
    'admin_config': 'sqlite:///' + join(DB_PATH, 'admin_config.db'),
    'logs':         'sqlite:///' + join(DB_PATH, 'logs.db'        ),
    'users':        'sqlite:///' + join(DB_PATH, 'users.db'       )
}

PANEL_EXT = False # Activate Ext Alarm module
PANEL_NOX = True  # Activate Nox Alarm module

VENDOR_LOCAL = True  # True: Get css and js from local (False: from cdn provider)

# Detect env from filesystem location (Prod/Dev)
if ENVNAME == 'Dev' :
    ENV                     = 'development'
    APP_NAME                = 'DEV Home Alarm'
    DEBUG                   = True
    TEMPLATES_AUTO_RELOAD   = True
    # PORT = 5000 # No need to override of default port

elif ENVNAME == 'Prod':
    ENV                     = 'production'
    APP_NAME                = 'Home Alarm'
    DEBUG                   = False
    BCRYPT_LOG_ROUNDS       = 13 # Complexity of the encryption
