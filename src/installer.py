# -*- coding: ISO-8859-1 -*-
# -*- coding: utf-8 -*-
import subprocess

import os, click, sys, time
from os.path import join as join

import shutil
import filecmp
from datetime import datetime, timedelta
from time import sleep
import config
from utils.util_date import pretty_date

# Project Paths
project_name = 'home_alarm'
dev_root     = '/home/pi/Dev'
prod_root    = '/home/pi/Prod'
# /home/pi/Dev/home_alarm/
dev_path     = join(dev_root, project_name)
# /home/pi/Prod/home_alarm/
prod_path    = join(prod_root, project_name)
# /home/pi/Dev/home_alarm_CONFIG/
dev_config_path  = join(dev_root, project_name + '_CONFIG')
# /home/pi/Prod/home_alarm_CONFIG/
prod_config_path  = join(prod_root, project_name + '_CONFIG')
# /home/pi/Prod/home_alarm_LOG/
log_path     = join(prod_root, project_name + '_LOG')
# /home/pi/Prod/home_alarm_LOG.bak/
log_path_bak = join(prod_root, project_name + '_LOG.bak')

# Config Paths & Files
nginx_conf   = 'etc/nginx/sites-enabled/home_alarm.nginx'
nginx_conf_source = join(dev_config_path, nginx_conf)
nginx_conf_dest   = join('/',         nginx_conf)
supervisor_config_path  = '/etc/supervisor/conf.d/'
supervisor_config_file  = 'supervisor_alarm_prod.conf'

# Commands
nginx_status        = 'sudo service nginx status'
nginx_start         = 'sudo service nginx start'
nginx_stop          = 'sudo service nginx stop'
nginx_restart       = 'sudo service nginx restart'
supervisor_restart  = 'sudo supervisorctl restart prod:*'
supervisor_start    = 'sudo supervisorctl start prod:*'
supervisor_stop     = 'sudo supervisorctl stop prod:*'
supervisor_status   = 'sudo supervisorctl status'
rmdir_log_bak       = 'rm -Rf {}'.format(log_path_bak)
mv_log_bak          = 'mv {} {}'.format(log_path, log_path_bak)
mkdir_log           = 'mkdir {}'.format(log_path)


def print_path_warning():
    log.warning('Will remove all content in '+root_prod_path + project_name)

@click.group()
def installer():
    pass

@click.group()
def deploy_from_dev(): pass
installer.add_command(deploy_from_dev)

@click.group()
def deploy_from_git(): pass
installer.add_command(deploy_from_git)


#########
# Utils #
#########

def cmpfiles(f1, f2):
    """ Compare two files
    Return True if files are equal, else return false
    'shallow=True' then same os.stat is enough to consider the files as equal
    """
    try:
        result = filecmp.cmp(f1, f2, shallow=True)
        log.debug('Diff {} {} {}'.format(result, f1, f2))
    except FileNotFoundError:
        log.warning('File not found')
        result = False
    return (result)

def rmfile(file_path, disable_log=None):
    """ Remove a file
    'disable_log' allow to replace logger with print
    """
    if (not disable_log): log.debug('Deleting file ' + file_path)
    try:
        os.remove(file_path)
    except OSError as e:
        if (not disable_log): log.exception('%s - %s.' % (e.filename, e.strerror))
        else: print('%s - %s.' % (e.filename, e.strerror))
        
def rmdir(dir_path):
    log.debug('Deleting dir ' + dir_path)
    try:
        shutil.rmtree(dir_path)
    except OSError as e:
        log.exception('%s : %s' % (dir_path, e.strerror))
        
def copydir(src, dest, ignore=None):
    log.debug('Copying ' + src + ' -> ' + dest)
    try:
        shutil.copytree(src, dest, ignore=ignore)
    except OSError as e:
        log.exception('%s' % (e.strerror))        

def copyfile(src, dest):
    log.debug('Copying ' + src + ' -> ' + dest)
    try:
        shutil.copy(src, dest)
    except OSError as e:
        log.exception('%s' % (e.strerror))        

################
# nginx status # 
################
def nginx_status():
    """Parse nginx status, return a string saying uptime or dead
    """
    cmd = """sudo service nginx status"""
    try:
        stdout = execute_check_output(cmd)
        result = stdout.splitlines()[2] # get third line
    except:
        result = 'dead'
    return (result)
    
def execute_check_output(cmd):
    """ Execute commande, return output
    """
    # cmd = """cat /etc/hostname"""
    log.debug('command %s' % (cmd))
    stdout = subprocess.check_output(cmd, shell=True)
    stdout = stdout.decode('utf-8')
    return (stdout)
    
def execute(cmd, disable_log=None):
    """ Execute commande, print output in console
    """
    if not disable_log: log.debug('command %s' % (cmd))
    else: print('command %s' % (cmd))
    proc = subprocess.Popen (cmd.split(' '), shell=False)
    proc.communicate()
    
@installer.command()
def deploy_from_dev():
    """ Deploy from /home/pi/Dev directory
    Copy content of Dev/home_alarm in Prod/home_alarm 
    Restart supervisor
    Update nginx config (if needed) and restart nginx
    """
    now = pretty_date(format = 'long')
    log.warning(' ------------------- ')
    log.warning('|  Deploy From Dev  |')
    log.warning(' ------------------- ')
    log.warning('|  '+ now +' |')
    log.warning(' ------------------- ')

    
    log.info('Copy project and config')
    # Copy project path
    rmdir(prod_path)
    copydir(dev_path, prod_path, \
       ignore=shutil.ignore_patterns('.git*', '__pycache__'))
    
    # Copy project_CONFIG path
    rmdir(prod_config_path)
    copydir(dev_config_path, prod_config_path, \
       ignore=shutil.ignore_patterns('.git*', '__pycache__'))
    
    # Update nginx config if needed
    log.info('Check nginx config ...')
    if (cmpfiles(nginx_conf_source, nginx_conf_dest)):
        log.info('No conf update needed')
    else:
        log.info('Conf update')
        execute('sudo rm %s' % (nginx_conf_dest))
        execute('sudo cp %s %s' % (nginx_conf_source, nginx_conf_dest))
        execute('sudo nginx -t')
    
    log.info('Stop nginx / Supervisor ...')
    execute(supervisor_stop)
    execute(nginx_stop)
    
    log.info('Backup log and clean log folder ...')
    sleep(1)
    execute(rmdir_log_bak)
    execute(mv_log_bak)
    execute(mkdir_log)
    # rmdir(log_path_bak)
    # copydir(log_path, log_path_bak)

    log.info('Start nginx / Supervisor ...')
    execute(nginx_start)
    execute(supervisor_start)
    log.info('Nginx status: %s' % (nginx_status()))
    execute(supervisor_status)

@installer.command()
def test():
    log.warning(' -------- ')
    log.warning('|  Test  |')
    log.warning(' -------- ')

    log.info("execute('sudo nginx -t')")
    execute('sudo nginx -t')
    log.info("execute_check_output('sudo nginx -t')")
    execute_check_output('sudo nginx -t')    
    
if __name__ == '__main__':
    """ Configure logger """
    import colorlog
    import logging
    from logging.config import dictConfig
    logfilename         = 'home_alarm_Deploy.log'
    logfile             = join(prod_root, logfilename)

    log_colors = { 'DEBUG':'cyan', 'INFO':'green','WARNING':'yellow', 'ERROR':'red', 'CRITICAL':'red,bg_white' }
    log_settings = {
        'version': 1,
        'formatters': { 'simple': {
                '()': 'colorlog.ColoredFormatter',
                'log_colors': log_colors,
                'format': '%(log_color)s%(levelname)-8s | %(message)s' } },
        'handlers': {
            'stdout': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
                'formatter': 'simple' },
            'file': {
                'level': 'DEBUG',
                'formatter': 'simple',
                'class': 'logging.FileHandler',
                'filename': logfile,
                'mode': 'w' } },
        'root': {
            'level': 'DEBUG',
            'handlers': ['stdout', 'file'] } }
            
    dictConfig(log_settings)
    log = logging.getLogger(__name__)
    
    """ Execute the programm """
    installer()
  