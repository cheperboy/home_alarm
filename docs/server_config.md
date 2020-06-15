# Server configuration

## Virtualenv wrapper

[about python3 and virtualenvwrapper](https://medium.com/@gitudaniel/installing-virtualenvwrapper-for-python3-ad3dfea7c717)

## Installation steps

1. Install raspbian
2. configure wifi (edit  `/etc/wpa_supplicant/wpa_supplicant.conf`)
3. set hostname to alarm (edit  `/etc/hostname` and `/etc/hosts`. raspberry will be accessible via *http://alarm*)
4. `mkdir /home/pi/Dev && cd /home/pi/Dev`
5. `git clone https://github.com/cheperboy/home_alarm.git`
6. Create secret config json files in `home_alarm/src/etc`
8. `(dev) pi@alarm:~/Dev/home_alarm/src $ python installer.py deploy-from-dev`
9. Create an admin user

	`(dev) pi@alarm:~/Dev/home_alarm/src $ python manager.py users create`

## Software config files

| dir | File | Content |
| --- | ---- | ----- |
| src/etc/ 	 | `flask_config_secret.json` 	| Flask app 										|
| src/etc/ 	 | `email_config_secret.json` 	| Gmail SMTP and account config |
| src/etc/ 	 | `sms_config_secret.json` 		| Nexmo Gateway API key 				|
| src/etc/ 	 | `nox_unipi_io.json` 					| System Hardware I/O config		|
| src/utils/ | `logger_config.py`						| App logger config 						|
| etc/			 | `supervisor_alarm_prod.conf`	| supervisor production 				|
| etc/			 | `supervisor_alarm_dev.conf`	| supervisor for dev purpose 		|
| etc/nginx/ | `home_alarm` 								| App nginx server conf 				|
| etc/nginx/ | `evok` 											| evok nginx server conf 				|


## Software directories

``` bash
~/{Dev|Prod}/home_alarm
~/{Dev|Prod}/home_alarm_DB
~/{Dev|Prod}/home_alarm_LOG
~/Prod/home_alarm_SSL
```

## Scripts

| script 				| section 	| function 	| desc 	|
| ------ 				| ----- 		| ----- 		|				|
| `manager.py` 	| 					| 					|				|
| 							| users 		| 		 			| 			|
| 							| 		 			| create 		| Create an admin user			|
| 							| 		 			| delete 		| user delete --name toto 	|
| 							| 		 			| list 			| List admin users					|
| 							| database 	| 		 			| 													|
| 							| 		 			| init 			| Recreate the db tables except the one specified with cli option	|
| 							| 		 			| init-all 	| Recreate All the db tables. 	|
| 							| 		 			| logs 			| List DBLog entries						|
| `installer.py`|  					| 								| 												|
|  							|  					| deploy_from_dev	| Copy content of /Dev/home_alarm in /Prod/home_alarm	|
| 			 				|  					| deploy_from_git	| Not implemented					|


## SSL Certificate

```sh
cd /home/pi/Prod/home_alarm_SSL
openssl req -x509 -newkey rsa:4096 -nodes -out certificate.pem -keyout private_key.pem -days 365
```

## supervisor

Add at the end of `/etc/supervisor/supervisord.conf`

``` bash
[include]
files = /etc/supervisor/conf.d/*.conf /home/pi/Prod/home_alarm_CONFIG/etc/supervisor_alarm_prod.conf /home/pi/Dev/home_alarm_CONFIG/etc/supervisor_alarm_dev.conf
```

!!! warning ""
	/home/pi/**Prod**/home_alarm/etc/supervisor_alarm_**prod**.conf /home/pi/**Dev**/home_alarm/etc/supervisor_alarm_**dev**.conf


## nginx

`sudo nginx -t` - Check configuration  
`sudo service nginx restart` - Restart nginx

### flask web app

Create a home_alarm conf file and sym link

``` bash
 sudo cp ~/Prod/home_alarm/etc/nginx/sites-enabled/home_alarm /etc/nginx/sites-enabled/home_alarm
```

Remove the sym link to default conf file (otherwise it causes errors)  
`sudo rm /etc/nginx/sites-enabled/default`

### evok

Modify evok config to listen port 81 instead of 80 and only localhost interface.

Change:
```
listen 80 default_server;
server_name  _;
```
to:
```
listen 127.0.0.1:81;
```

Use following commands:
``` bash
sudo rm /etc/nginx/sites-enabled/evok
sudo cp ~/Prod/home_alarm/etc/nginx/evok /etc/nginx/sites-enabled/
```

## Supervisor
Modify supervisor service configuration to include the conf file of the Alarm software (`/home/pi/Prod/home_alarm/etc/supervisor_alarm.conf`)

Append the file path at the end of `/etc/supervisor/supervisord.conf`

```
[include]
files = /etc/supervisor/conf.d/*.conf /home/pi/Prod/home_alarm/etc/supervisor_alarm.conf
```

To start alarm deamons (flask and noxAlarmProcess):

``` bash
sudo supervisorctl reread
sudo supervisorctl reload
sudo supervisorctl start prod:*
```
