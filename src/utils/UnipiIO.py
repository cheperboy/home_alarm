"""
UnipiInput() and UnipiOutput() provide access to evok rest API
for this project, evok is configured to listen on port 81 (/etc/evok-nginx.conf)
Two different method are used. Could be harmonized:
UnipiInput() calls evok with requests.get(req_url)
UnipiOutput() calls evok with check_output(command, shell=True)
Flag 'PRINT_BEBUG' can be set to print more debug info
"""
PRINT_BEBUG = True
# PRINT_BEBUG = None

import sys
import json
import requests
from subprocess import check_output
from time import sleep
import logging

""" Configure logger """
logger = logging.getLogger('alarm.utils.unipi')

BASE_URL = "http://localhost:81/rest" # evok rest API URL

class UnipiInput():
    def __init__(self, json_config):
        logger.debug('Configuring intput %s %s' % (json_config['name'], json_config['circuit']))
        self.name    = str(json_config['name'])
        self.circuit = str(json_config['circuit'])  # Unipi input number
        self.inverse = json_config['inverse']       # Input is active low (0v)
        self.value = None                           # Set to 0/1 after reading
        
    def read(self):
        """
        Sends a GET request to retrive digital input state
        Set self.value (consider inverse value if input active low)
        Returns False (error) or True (success)
        """
        try:
            req_url = BASE_URL + "/input/" + self.circuit
            r = requests.get(req_url)
            if r.status_code == 200:
                if self.inverse == True:
                    # Inverse the value if input is active low
                    self.value = 0 if r.json()['value'] == 1 else 1
                else:
                    self.value = r.json()['value']
                return (True)
            else:
                # Error reading value.
                logger.error('evok read input request failed %s %s' % (req_url, r))
                # TODO Monitor this error (how much a day?) and implement right action (self.valid=False)
                return(False)
        except Exception as e:
            logger.exception('evok read input failed %s' % (e))
            return(None)
       
class UnipiOutput():
    PULSE_DELAY = 0.75 # delay for impulse output
    
    # def print_state(self):
        # print(slef.name + ' ' + str(self.value))
    
    def __init__(self, json_config):
        logger.debug('Configuring output %s %s' % (json_config['name'], json_config['circuit']))
        self.name    = str(json_config['name'])
        self.circuit = str(json_config['circuit'])
        self.impulse = json_config['impulse']  # impulse => output is always low and goes high during 0,7s output is activate.
        self.value   = self.read()  # 0 or 1

    def read(self):
        """
        Sends a GET request to retrive relay state
        Returns False (error) or True (success)
        """
        try:
            req_url = BASE_URL + "/relay/" + self.circuit
            r = requests.get(req_url)
            if r.status_code == 200:
                self.value = r.json()['value']
                return (True)
            else:
                # Error reading value.
                logger.error('evok read output request failed %s %s' % (req_url, r))
                return(False)
        except Exception as e:
            logger.exception('evok read output failed %s' % (e))
            raise e
            return(None)

    def set_relay(self, value):
        """ Sends a POST request via command line
        circuit: id of the relay (1 to 8)
        value: 1->On, 0->Off
        command: wget -qO- http://alarm.local/rest/relay/1 --post-data='value=0'
        """
        logger.debug('evok set relay %s %s' % (self.name, value))
        try:
            command = "wget -qO- "+ BASE_URL + "/relay/"+str(self.circuit)+" --post-data='value="+str(value)+"'"
            if PRINT_BEBUG: logger.debug('request %s' % (command))
            response = check_output(command, shell=True).decode('utf-8')
            if PRINT_BEBUG: logger.debug('response %s' % (response))
            json_response = json.loads(response)
            # If answer = 200 and value read from relay is as expected then set the value of the class object and return True
            if json_response['success'] == True and json_response['result'] == value:
                self.value = value
                return(True)
            else:
                # TODO Shoud log failure when command relay
                logger.error('evok request failed %s %s' % (command, response))
                return(None)
        except Exception as e:
            logger.exception('evok set_relay failed %s' % (e))
            return(None)
            
    def pulse(self):
        """ pulse high during DELAY then goes back to low
        """
        logger.debug('evok pulse relay %s' % (self.name))
        if self.set_relay(1):
            sleep(self.PULSE_DELAY)
            if self.set_relay(0):
                return(True) # Success
        logger.critical('evok fail pulse relay %s' % (self.name))
        return(None)
        