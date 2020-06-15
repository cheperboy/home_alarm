from os.path import abspath as abspath
from os.path import dirname as dirname
from os.path import join    as join
import sys, json

import logging
import nexmo                    # SMS Provider
from subprocess import call     # to execute a shell command
from threading  import Thread   # to launch an async thread
from datetime   import datetime

from utils.util_date     import pretty_date
from utils.config_helper import env_config_from_json
from utils.emails        import EmailNexmoBalance # for low nexmo balance alert

logger = logging.getLogger('alarm.utils.sms')

conf_filename = 'sms_config_secret.json'     # Shall include *secret* for gitignore
module        = abspath(dirname(__file__))   # Absolute path of the directory where this program resides
src           = abspath(dirname(module))     # Absolute path of the parent directory
project       = abspath(dirname(src))        # Absolute path of the parent directory
env           = abspath(dirname(project))    # Absolute path of the parent directory
conf_file     = join(env, 'home_alarm_CONFIG/', 'software/', conf_filename)


class SmsGateway():
    """ Gateway to Nexmo SMS provider.
    This class provides a simple method send(text_body) 
    This class gets configuration from json secret file
    Example of call: SmsGateway().send(text_body)
    exemple of content of secte conf file
    {
        "common" : {
            "NEXMO_API_KEY"    : "foo",
            "NEXMO_API_SECRET" : "bar"
            "ADMIN_PHONES"     : ["33600000000"]
        },
        "production" : {
            "USERS_PHONES"     : ["33600000000"]
        },
        "development" : {
            "USERS_PHONES"     : ["33600000000"]
        }
    }
    """    
    
    def __init__(self):
        # Load secret config (API Key, phone numbers)
        try:
            self.conf = env_config_from_json(conf_file)
        except Exception as e:
            logger.exception('Init sms conf failed')
            raise
        
        # Create Nexmo instance
        try:
            self.provider = nexmo.Client(key=self.conf['NEXMO_API_KEY'], secret=self.conf['NEXMO_API_SECRET'])
        except Exception as e:
            logger.exception('Init Nexmo failed')
            raise
        
    def send(self, body, admin_only=None):
        """ Start Thread to send asynchronously
        """
        if (admin_only):
            recipients = self.conf['ADMIN_NUMBER']
        else:
            recipients = self.conf['RECIPIENTS_NUMBER']
        
        thread = Thread(target=self.thread_send, args=[body, recipients])
        thread.start()
        
    def thread_send(self, body, recipients):
        """ Call Nexmo API to send SMS 
        https://developer.nexmo.com/api/sms?utm_source=DEV_REL&utm_medium=github&utm_campaign=python-client-library#send-an-sms
        """
        try:
            for recipient in recipients:            
                sms         = {}
                sms['from'] = self.conf['SENDER_NAME']
                sms['to']   = recipient
                sms['text'] = body
                logger.debug(str(sms))
                http_response = self.provider.send_message(sms)
                response = http_response['messages'][0]
                if response['status'] == '0':
                    logger.info('SMS sent to %s' % (recipient))
                else:
                    logger.error('SMS Fail to %s Error: %s' % (recipient, response['error-text']))
            
            # log nexmo balance
            balance = '%.1f' % (float(response['remaining-balance']))
            logger.info('Remaining balance is %s' % (balance))
        except Exception as e:
            logger.exception('Failed sending SMS')
        
        # Email the balance value to admin
        try: EmailNexmoBalance(response['remaining-balance'])
        except: pass

class SmsAlarmAlert():
    """ This class sends SMS Alert from Alarm Processes.
    This class rely on SmsGateway() Class
    example of call: SmsAlarmAlert("Info", "Nox", "started")
    """
    def __init__(self, level, module, event):
        """ Send Sms from Alarm System.
        level: Info / Alert / Error
        module : Nox / Ext / Other
        event : started / stopped / detection
        """
        try:
            date = pretty_date(datetime.now())
            self.sms_gateway = SmsGateway()
            body = "Home Alarm %s %s %s %s" % (level, module, event, date)
            logger.debug('Sending SMS %s' % (body))
            self.sms_gateway.send(body)
        except:
            logger.exception("Error when sending sms")
            return
            