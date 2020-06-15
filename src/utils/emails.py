from os.path import abspath as abspath
from os.path import dirname as dirname
from os.path import join    as join
import sys, json
import smtplib, ssl             # Email lib
from email.message import EmailMessage

from subprocess import call     # to execute a shell command
from threading import Thread    # to launch an async thread
from datetime import datetime

from utils.util_date import pretty_date
from utils.config_helper import env_config_from_json

import logging
logger = logging.getLogger('alarm.utils.emails')

conf_filename = 'email_config_secret.json'   # Shall include *secret* for gitignore
module        = abspath(dirname(__file__))   # Absolute path of the directory where this program resides
src           = abspath(dirname(module))     # Absolute path of the parent directory
project       = abspath(dirname(src))        # Absolute path of the parent directory
env           = abspath(dirname(project))    # Absolute path of the parent directory
conf_file     = join(env, 'home_alarm_CONFIG/', 'software/', conf_filename)

# Emoji unicode from https://unicode.org/emoji/charts/full-emoji-list.html
EMOJI = {}
EMOJI['stop_sign']        = "\U0001F6D1" # 🛑
EMOJI['high_voltage']     = "\U000026A1" # ⚡
EMOJI['police_car_light'] = "\U0001F6A8" # 🚨
EMOJI['warning']          = "\U000026A0" # ⚠
EMOJI['no_entry']         = "\U000026D4" # ⛔
EMOJI['check_mark']       = "\U00002714" # ✔
EMOJI['loudspeaker']      = "\U0001F4E2" # 📢
EMOJI['telephone']        = "\U0000260E" # ☎


class EmailGateway():
    """ Gateway to gmail smtp.
        This class provides a simple method send(subject, text_body) 
        This class gets configuration from json secret file
        Example of call: EmailGateway().send(subject, text_body)
        exemple of content of secte conf file
        {
            "Common" : {
                "MAIL_SERVER" 	: "smtp.gmail.com",
                "MAIL_PORT" 	: 465,
                "MAIL_USERNAME" : "foo@gmail.com",
                "MAIL_PASSWORD" : "foo",
                "MAIL_NAME"     : "Alarm",
                "ADMIN_EMAILS" 	: ["foo@gmail.com"]
            },
            "Prod" : {
                "USERS_EMAILS" :  ["foo@gmail.com"],
                "USERS_PHONES" :  ["336000000"]
            },
            "Dev" : {
                "USERS_EMAILS" :  ["foo@gmail.com"],
                "USERS_PHONES" :  ["336000000"]
            }
        }
    """    
    
    def __init__(self):
        try:
            self.conf = env_config_from_json(conf_file)
        except Exception as e:
            logger.exception('Init mail conf failed')
            raise # to be catch by caller
        
    def send(self, subject, text_body, admin_only=None):
        """ Start Thread to send asynchronously
        """
        if (admin_only):
            recipients = self.conf['ADMIN_EMAILS']
        else:
            recipients = self.conf['USERS_EMAILS']
        thr = Thread(target=self.thread_send, args=[subject, text_body, recipients])
        thr.start()
        
    def thread_send(self, subject, text_body, recipients):
        msg = EmailMessage()
        msg.set_content(text_body)
        msg['Subject'] = subject
        msg['From'] = self.conf['MAIL_NAME']
        # msg['To'] = ', '.join(self.conf['USERS_EMAILS'])
        msg['To'] = ', '.join(recipients)
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.conf['MAIL_SERVER'], self.conf['MAIL_PORT'], context=context) as server:
                server.login(self.conf['MAIL_USERNAME'], self.conf['MAIL_PASSWORD'])
                server.send_message(msg)
        except Exception as e:
            logger.exception('Failed sending email')
    
    def test(self):
        date = pretty_date(datetime.now())
        subject     = "Home alarm Test Mail {0}".format(date)
        text_body   = "Test content."
        logger.info('Sending test email')
        self.send(subject, text_body, admin_only=True)

        
class EmailAlarmAlert():
    """ This class provide methods to send email alerts from Alarm Processes.
    This class rely on EmailGateway() Class
    example of call: EmailAlarmAlert("Info", "Nox", "started")
    """
    def __init__(self, level, module, event, admin_only=None):
        """ 
        level: Info / Alert / Error
        module : Nox / Ext / Other
        event : started / stopped / detection
        """
        try: self.email_gateway = EmailGateway()
        except:
            logger.warning('Abort email alert')
            return

        try:
            self.icons = {}
            self.icons['Info']  = EMOJI['check_mark']
            self.icons['Alert'] = EMOJI['stop_sign']
            self.icons['Error'] = EMOJI['high_voltage']
            icon = self.icons[level]
        except:
            logger.warning('Emoji non blocking issue')
            icon = ''
        
        try:
            date = pretty_date(datetime.now())
            text = "Home Alarm %s %s %s %s" % (level, module, event, date)
            text_body   = text
            subject     = "%s %s" % (icon, text)
            logger.info('Sending email %s' % (subject))
            self.email_gateway.send(subject, text_body, admin_only=admin_only)
        except:
            logger.exception("Error when sending email")
            return
           
class EmailNexmoBalance():
    """ Send email if nexo balace is low.
    This class rely on EmailGateway() Class
    example of call: EmailAlarmAlert("Info", "Nox", "started")
    """
    def __init__(self, nexmo_balance):
        try: self.email_gateway = EmailGateway()
        except:
            logger.warning('Abort sending EmailNexmoBalance')
            return
        
        try: icon = EMOJI['loudspeaker']
        except:
            logger.warning('Emoji non blocking issue')
            icon = ''
        
        try:
            balance = '%.1f' % (float(nexmo_balance))
            date = pretty_date(datetime.now())
            text = "Nexmo balance %s" % (balance)
            text_body   = text
            subject     = "%s %s" % (icon, text)
            logger.info('Sending email to admin %s' % (subject))
            self.email_gateway.send(subject, text_body, admin_only=True)
        except:
            logger.exception("Abort sending EmailNexmoBalance")
            return

if __name__ == '__main__':
    """ Used only for testing purpose
    """
    print("Testing module {}".format(__file__))
    email_gateway = EmailGateway()
    print (email_gateway.conf)
    # EmailAlarmAlert("Info", "Nox", "started")

