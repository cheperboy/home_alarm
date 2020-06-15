"""
Defines sockets ports and constant considering path based environnement (Dev/Prod)
Topic/Command constants are common whatever the environnement
Only the ports differs to allow both servers dev/prod running at the same time
"""

import os, sys

filepath = os.path.abspath(os.path.dirname(__file__)) # /home/pi/Dev/home_alarm/src/ext_alarm
env      = filepath.split("/")[3]                     # Dev / Prod
# env      = filepath[9:12]                           # Dev / Pro

# --- Common configuration ---
# Socket extalarm Command
TOPIC_COMMAND = "1"
COMMAND_START = "1"
COMMAND_STOP = "2"

# Socket extalarm State
TOPIC_EVENT     = "1"
TOPIC_STATE     = "2"

# --- Development configuration ---
if env == 'Dev' :
    port_socket_extalarm_command = "5556"   # Socket extalarm Command
    port_socket_extalarm_state   = "5557"   # Socket extalarm State

# --- Production configuration ---
elif env == 'Prod':
    port_socket_extalarm_command = "5558"  # Socket extalarm Command
    port_socket_extalarm_state   = "5559"  # Socket extalarm State

else:
    print ("config ERROR")
    