# -*- coding: utf-8 -*-
import subprocess
import re
from flask import current_app as app
from web import db

#########
# Nexmo #
#########

from os.path import abspath as abspath
from os.path import dirname as dirname
from os.path import join    as join
from utils.config_helper import env_config_from_json
conf_filename = 'sms_config_secret.json'     # Shall include *secret* for gitignore
module        = abspath(dirname(__file__))   # Absolute path of the directory where this program resides
web           = abspath(dirname(module))     # Absolute path of the parent directory
src           = abspath(dirname(web))     # Absolute path of the parent directory
project       = abspath(dirname(src))        # Absolute path of the parent directory
env           = abspath(dirname(project))    # Absolute path of the parent directory
conf_file     = join(env, 'home_alarm_CONFIG/', 'software/', conf_filename)

import nexmo
def nexmo_balance():
    try:
        nexmo_conf = env_config_from_json(conf_file)
    except Exception as e:
        app.logger.exception('Init Nexmo conf failed')
        return ('')
    
    nexmo_client = nexmo.Client(key=nexmo_conf['NEXMO_API_KEY'], secret=nexmo_conf['NEXMO_API_SECRET'])
    try:
        result = nexmo_client.get_balance()    
        balance = "{:.2f}".format(result['value'])
        balance = str(balance) + " €"
    except Exception as e:
        app.logger.warning('Retrieve Nexmo balance failed')
        return ('?')
    return (balance)

###########
# Network #
###########
def hostname():
    cmd = """cat /etc/hostname"""
    stdout = subprocess.check_output(cmd, shell=True)
    stdout = stdout.decode('utf-8')
    return (stdout)

def ip_lan_eth():
    cmd = """ifconfig eth0 | grep 'inet ' | awk '{print $2}' """
    stdout = subprocess.check_output(cmd, shell=True)
    stdout = stdout.decode('utf-8')
    return (stdout)

def ip_lan_wifi():
    cmd = """ifconfig wlan0 | grep 'inet ' | awk '{print $2}' """
    stdout = subprocess.check_output(cmd, shell=True)
    stdout = stdout.decode('utf-8')
    return (stdout)

##############
# Supervisor #
##############
def supervisor_status():
    """
    """
    cmd = '''sudo supervisorctl status'''
    stdout = subprocess.check_output(cmd, shell=True)
    stdout = stdout.decode('utf-8')
    procs = stdout.splitlines() # each line is a process
    result = {}
    for proc in procs:
        proc = re.sub('\s+', ' ', proc).strip() #replace multiple spaces by one space
        splitted_proc = proc.split(' ')
        name = splitted_proc.pop(0)
        status = splitted_proc.pop(0)
        uptime = ' '.join(splitted_proc)
        result[name] = status + '  ' + uptime
    return (result)

#########
# nginx # 
#########
def service_nginx_status():
    """Parse nginx status, return a string saying uptime or dead
    """
    cmd = '''sudo service nginx status'''
    try:
        stdout = subprocess.check_output(cmd, shell=True)
        stdout = stdout.decode('utf-8')
        result = stdout.splitlines()[2] # get third line
    except:
        result = "dead"
    return (result)

#########
# evok # 
#########
def service_evok_status():
    """Parse evok status, return a string saying uptime or dead
    """
    cmd = '''sudo service evok status'''
    try:
        stdout = subprocess.check_output(cmd, shell=True)
        stdout = stdout.decode('utf-8')
        result = stdout.splitlines()[2] # get third line
    except:
        result = "dead"
    return (result)

##############
# supervisor # 
##############
def service_supervisor_status():
    """Parse supervisor status, return a string saying uptime or dead
    """
    cmd = '''sudo service supervisor status'''
    try:
        stdout = subprocess.check_output(cmd, shell=True)
        stdout = stdout.decode('utf-8')
        result = stdout.splitlines()[2] # get third line
    except:
        result = "dead"
    return (result)

##########
# System #
##########
def system_uptime():
    """
    """
    cmd = '''uptime -p'''
    stdout = subprocess.check_output(cmd, shell=True)
    stdout = stdout.decode('utf-8')
    return (stdout)

def system_date():
    """
    """
    cmd = '''date'''
    stdout = subprocess.check_output(cmd, shell=True)
    stdout = stdout.decode('utf-8')
    return (stdout)

def cpu_temp():
    """
    The shell command (vcgencmd measure_temp) returns
    temp=64.5'C
    This function returns
    64.5'C
    """
    cmd = '''vcgencmd measure_temp'''
    stdout = subprocess.check_output(cmd, shell=True)
    stdout = stdout.decode('utf-8')
    stdout = stdout.split("=")
    return(stdout[1])

def disk_space():
    """
    The shell command (df with options...) returns
    /dev/root          7,0G    3,5G  52%
    This function returns
    {'cpu_temp': '7,0G', 'used': '3,5G', 'used_percent': '52%'}    
    """
    cmd = '''df -h --output=source,size,used,pcent | grep /dev/root'''
    stdout = subprocess.check_output(cmd, shell=True)
    stdout = stdout.decode('utf-8')
    stdout = stdout.split( )
    size         = stdout[1]                # string like '29G' 
    used         = stdout[2]                # string like '3.1G'
    used_percent = stdout[3]                # string like '25%'
    meter_value = str(int(stdout[3][:-1]))  # string like '25'
    # meter  = ' <meter value="'+ meter_value +'"></meter>'
    meter  = '<div class="progress"> <div class="progress-bar" role="progressbar" style="width: 25%;" aria-valuenow="'+meter_value+'" aria-valuemin="0" aria-valuemax="100">'+used_percent+'</div></div>'
    
    ret = {
        "used_percent" : meter,
        "size"         : size, 
        "used"         : used, 
    }
    return (ret)
    
#################
# Database size #
#################
def db_size():
    """
    The command returns:
        EMPTY LINE
        app.db 0
        chaudiere.db 536576
        chaudiere_hour.db 8192
        chaudiere_minute.db 241664        
    This function returns:
        {'app.db': '0 Mo', 'chaudiere.db': '537 Mo', 'chaudiere_hour.db': '8 Mo', 'chaudiere_minute.db': '242 Mo'}
    """
    
    cmd = """ls -l """+app.config['DB_PATH']+""" | awk '{ print $9 " " $5 }' """
    stdout = subprocess.check_output(cmd, shell=True)
    stdout = stdout.decode('utf-8')
    ret = {}
    for line in stdout.splitlines():
        line = line.split( )
        if len(line) > 0:
            size = '{:.2f}'.format(float(line[1])/(1000*1000))
            size = str(size) + " Mo"
            ret[line[0]] = size
    return (ret)

############
# Log size #
############
def log_size():
    """
    The command returns:
        EMPTY LINE
        app.db 0
        chaudiere.db 536576
        chaudiere_hour.db 8192
        chaudiere_minute.db 241664        
    This function returns:
        {'app.db': '0 Mo', 'chaudiere.db': '537 Mo', 'chaudiere_hour.db': '8 Mo', 'chaudiere_minute.db': '242 Mo'}
    """
    cmd = """ls -l """+app.config['LOG_PATH']+""" | awk '{ print $9 " " $5 }' """
    stdout = subprocess.check_output(cmd, shell=True)
    stdout = stdout.decode('utf-8')
    ret = {}
    for line in stdout.splitlines():
        line = line.split( )
        if len(line) > 0:
            size = '{:.2f}'.format(float(line[1])/(1000*1000))
                    
            size = str(size) + " Mo"
            ret[line[0]] = size
    return (ret)

    