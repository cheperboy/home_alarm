## logging

supervisor -> daemon.py -> script.py

* daemon.py implements a while(1) loop
* daemon.py call app logger
* script.py call app logger

1/  

* daemon.py and script.py will respect app logger config (rotation, log file naming, log level), whatever [program:daemon] supervisor conf

2/  

* if no log conf is defined in [program:daemon] supervisor conf, (meaning stdout_logfile and stderr_logfile is redirected to /dev/null, then nothing else happens.
* if a log conf is defined in [program:daemon] supervisor conf, this will be respected besides app logger conf.

*Then:*  
* app logger can concatenate info from multiple scripts and daemons (supervisor cannot)
* specific log file can be produced related to a single daemon (and its subscripts)

*Conf for ChaudiereApp:*  

* app logger concatenate every damons logs
* no log conf in supervisor program conf