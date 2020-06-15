# -*- coding: ISO-8859-1 -*-
from gevent import monkey
monkey.patch_all()
# import eventlet
# eventlet.monkey_patch()

import os, click
from web import create_app, db
from utils.emails import EmailGateway, EmailAlarmAlert
from utils.sms    import SmsGateway,   SmsAlarmAlert
# from web.models   import User, DBLog
import config

@click.group()
def tester():
    pass

### Generic section example #######
# @click.group()
# def section(): pass
# tester.add_command(section)

# @section.command()
# def test():
    # """tester.py section test """
    # pass
#####################################

@click.group()
def gateway(): pass
tester.add_command(gateway)

@gateway.command()
def mail():
    """ Test EmailGateway from flask app context 
    Test EmailAlarmAlert() from flask app context """
    # print('starting test email Gateway')
    # EmailGateway().test()
    print('starting test email wrapper')
    EmailAlarmAlert("Info", "Nox", "started", admin_only=True)

@gateway.command()
def sms():
    """ Test EmailGateway from flask app context 
    Test EmailAlarmAlert() from flask app context """
    # print('starting test sms gateway')
    # SmsGateway().test()
    SmsAlarmAlert("Test", "Nox", "detection")

    
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        tester()

  