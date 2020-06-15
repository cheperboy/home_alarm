"""
This module defines sockets ports and constant considering path based environnement (Dev/Prod)
Topic/Command constants are common whatever the environnement
Only the ports differs to allow both servers dev/prod running at the same time
Principle:
    One can SUBscribe to some topics to receive data
    the PUBlisher will send a string "TOPIC_ID ' ' COMMAND_ID" (see example below)
    self.PUB_COMMAND.send_string(zmq_socket_config.TOPIC_REQUEST + " " + zmq_socket_config.COMMAND_STOP)
"""

import sys
from os.path import abspath as abspath
from os.path import dirname as dirname
import logging
logger = logging.getLogger('alarm.config')

filepath = abspath(dirname(__file__)) # /home/pi/Dev/home_alarm/src/ext_alarm
env      = filepath.split("/")[3]     # Dev / Prod

# --- Common configuration ---

# Socket noxalarm Command
# Used to send command ("start" or "stop") and to send request "status update"
# One topic is defined and 3 different command_ids
TOPIC_REQUEST = "1" # Topic_id
COMMAND_START = "2" # Command_id
COMMAND_STOP  = "3" # Command_id
STATUS_UPDATE = "4" # Command_id

# Socket noxalarm State
# Used to send the status (state and events) of the alarm
# Two topics are defined.
# the data is the value of the state/event (so not defined here but set when sending the data).
TOPIC_EVENT     = "4"
TOPIC_STATE     = "5"

# --- Development configuration ---
if env == 'Dev' :
    port_socket_noxalarm_command = "5560"   # Socket noxalarm Command
    port_socket_noxalarm_state   = "5561"   # Socket noxalarm State

# --- Production configuration ---
elif env == 'Prod':
    port_socket_noxalarm_command = "5562"  # Socket noxalarm Command
    port_socket_noxalarm_state   = "5563"  # Socket noxalarm State

else:
    logger.critical("env is not Dev|Prod")
