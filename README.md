# Home Alarm
[![Documentation Status](https://readthedocs.org/projects/alarm/badge/?version=latest)](https://alarm.readthedocs.io/en/latest/?badge=latest)
[![Python 3.7.3](https://img.shields.io/badge/python-3.7.3-blue.svg)](https://www.python.org/downloads/release/python-373/)

## Links
* wiki [alarm.rtfd.io/](https://alarm.readthedocs.io/)
* wiki host [readthedocs.org](https://readthedocs.org/projects/alarm)

## Features
* [Flask](https://flask.palletsprojects.com/) app interface to manage home alarm system
* Alarm events update web page via [python-socketio](https://python-socketio.readthedocs.io/en/latest)
* Alarm system monitored by separate process (interact with flask via [ZMQ](http://zguide.zeromq.org/page:all) socket PUB/SUB pattern)
* Hardware IO interface with [UniPi 1.1](https://www.unipi.technology/unipi-1-1-p36)
* IO command/control [evok REST API](https://github.com/UniPiTechnology/evok)
* Send Email and SMS alerts on alarm detection using [nexmo](https://www.vonage.com/developer-center/)


## Dev
* Start Flask App: `python src/main.py`
* Start alarm process: `python src/noxAlarmProcess.py`

## Project layout

```
├── docs/                                 # Mkdocs files (hosted readthedocs)
├── etc/                                  # Server config
│   ├── nginx/
│   │   └── sites-enabled/
│   │       ├── evok                      # Modif evok config (localhost:81)
│   │       └── home_alarm
│   ├── supervisor_alarm_dev.conf
│   └── supervisor_alarm_prod.conf
├── hardware/                             # Fritzing & hardware wiring
├── mkdocs.yml                            # Documentation config
├── README.md
└── src/                                  # Software source
    ├── config.py                         # Flask config (factory pattern)
    ├── manager.py                        # Manage app script (create db, admin used, ...)
    ├── installer.py                      # Installation script (deploy from git or local)        
    ├── installer.log
    ├── main.py                           # Flask web app main entry point
    ├── noxAlarmProcess.py                # Process statemachine Alarm (infinite loop)
    ├── requirements.txt                  # python dependancies
    ├── tester.py                         # Script for testing
    │
    ├── etc/                              # App Config files
    │   ├── email_config_secret.json
    │   ├── flask_config_secret.json
    │   ├── nox_unipi_io.json
    │   └── sms_config_secret.json
    ├── ext_alarm/                        # Ext alarm sources
    │   ├── ExtAlarmConfig.json
    │   ├── extMachine.py
    │   ├── socket_const.py
    │   └── thread.py
    ├── nox_alarm/                        # Nox alarm gateway and socket config
    │   ├── noxGateway.py
    │   └── zmq_socket_config.py
    ├── utils/                            # Utils (date, email, sms, Unipi IO)
    │   ├── config_helper.py
    │   ├── emails.py
    │   ├── logger_config.py
    │   ├── sms.py
    │   ├── UnipiIO.py
    │   ├── util_date.py
    │   └── util_request_ip.py
    └── web/                              # Flask App (factory pattern)
        ├── __init__.py               
        ├── models.py                     # Users, Logs
        ├── static/                       # css & javascript (socketio)
        ├── templates/                    # html
        └── views                         # Flask blueprints
            ├── admin.py
            ├── alarms_panel.py
            ├── ext.py
            ├── login.py
            ├── nox.py
            └── system_info.py
```
