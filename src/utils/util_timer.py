"""
Simple timer utility 
No callback, the user polls the timer status to know if isrunning, expired, stopped.
Timer can be ON (started_at > 0) or OFF (started_at equals 0)
Timer must be set to OFF by the user (call self.stop() that put started_at to 0)
"""
import logging
from time import time

""" Configure logger """
logger = logging.getLogger('alarm.utils.timer')

class Countdown():

    def __init__(self, name, delay):
        #logger.debug('Configuring timer with delay %s' % (delay))
        logger.debug('Configuring timer with delay %s' % (delay))
        self.name  = name
        self.delay = delay
        self.started_at = 0
        self.run = None
        
    def __str__(self):
        #status = 'stop' if self.started_at == 0 else 'running'
        if self.started_at == 0:
            status = 'off'
        else:
            status = '{:.0f}/{}'.format((time()-self.started_at), self.delay)
        return (status)

    def start(self):
        logger.debug('started timer %s' % (self.name))
        self.started_at = time()
    
    def stop(self):
        logger.debug('stoped timer %s' % (self.name))
        self.started_at = 0
    
    def has_expired(self):
        """ Return True if timer is running and has_expired 
        Return False if timer is runnion and not yet elapse
        """
        return(time() - self.started_at > self.delay)
    
    def is_running(self):
        """ Return True if timer is running 
        """
        return(self.started_at > 0)


if __name__ == "__main__": 
    t = Countdown("wait_out", 10)
    print(t)
    t.start()
    while(t.over() != True):
        print(t)
        if(time() - t.started_at > 5):
            t.started_at = time()

