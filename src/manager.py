# -*- coding: ISO-8859-1 -*-

import os, click, sys, time
from random import randint
from datetime import datetime, timedelta

import getpass
from werkzeug.security import generate_password_hash

from web import create_app, db
from web.models import User
import config

from web.models import User, DBLog
# import send_email_sms

@click.group()
def manager():
    pass

@click.group()
def database(): pass
manager.add_command(database)

@click.group()
def users(): pass
manager.add_command(users)

############
# Database #
############
@database.command()
def init_all():
    """Recreate All the db tables."""
    db.drop_all()
    db.create_all()

@database.command()
@click.option('--delete_users_db', prompt='Erase users db (y/n) ?')
@click.option('--delete_admin_config_db', prompt='Erase admin_config db (y/n) ?')
def init(delete_users_db, delete_admin_config_db):
    """Recreate the db tables except the one specified with cli option"""
    all_db_except_users_and_config = ['logs']
    db.drop_all(all_db_except_users_and_config)
    db.create_all(all_db_except_users_and_config)
    if delete_users_db == 'y':
        db.drop_all('users')
        db.create_all('users')
    if delete_admin_config_db == 'y':
        db.drop_all('admin_config')
        db.create_all('admin_config')
    print("Done")

@database.command()
def logs():
    """ List DBLog entries """
    for log in DBLog.all():
        print (str(log))
    
        
################
# Manage Users #
################
@users.command()
def list():
    """ List admin users """
    for user in User.all(User):
        print (user.id, user.name, user.email)
    
@click.option('--name')
@users.command()
def delete(name):
    """user delete --name toto """
    user = User.get_by_name(User, name)
    db.session.delete(user)
    db.session.commit()
    
@users.command()
def create():
    """ Create an admin user """
    print ("List of existing users :")
    for user in User.all(User):
        print (user.id, user.name, user.email)
    print ()
    print ("New user")
    print ('Enter name: ')
    name = input()
    print ('Enter email: ')
    email = input()
    password = getpass.getpass()
    assert password == getpass.getpass('Password (again):')

    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))
    db.session.add(new_user)
    db.session.commit()
    
    print ('User added.')

    
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        manager()
  