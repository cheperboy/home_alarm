# Home Alarm wiki

* [linux wiki](https://linux-wiki.readthedocs.io/)
* [code](https://github.com/cheperboy/home_alarm)

## Commands

* `python main.py` - run flask app in console (debug mode)
* `sudo supervisorctl status`
* `sudo supervisorctl start all` - gunicorn & alarm process
* `sudo service nginx start / stop` - serve web app
* `python manager.py database init_all` - Create all databases
* `python manager.py users create` - Create admin user
* `sudo systemctl status evok` - Check if evok is running

