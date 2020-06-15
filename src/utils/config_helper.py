import json
import os
import logging

logger = logging.getLogger('alarm.utils.json')

def dict_from_json_file(file):
        """ Reads json file settings and returns a dictionnary 
        Print error message for most known exception and raise to be catch at higher level
        """
        logger.debug("Loading file "+ file)
        try:
            with open(file) as data_file:
                settings = json.load(data_file)
                return settings
        except FileNotFoundError as e:
            logger.error('File Not Found %s' % (str(file)))
            raise
        except IOError as e:
            logger.exception('IOError %s' % (e))
            raise
        except ValueError as e:
            logger.error('ValueError %s' % (e))
            raise
        except Exception as e:
            logger.exception('%s' % (e))
            raise
            
def env_config_from_json(file, conf_dict={}):
        """ Create or Update dictionnary "conf_dict" with values defined in the json "file" given as parameter
        read "Common" section and "Dev" or "Prod" section depending on the json "file" path given as parameter
        """
        logger.debug("Loading file "+ file)
        Env = env_name()    # Dev / Prod
        try:
            # json_config = dict_from_json_file(file)
            with open(file) as data_file:
                json_config = json.load(data_file)
            for var in ['Common', Env]:
                conf_dict.update(json_config[var])
            return(conf_dict)
        except FileNotFoundError as e:
            logger.error('File Not Found %s' % (str(file)))
            raise
        except IOError as e:
            logger.exception('IOError %s' % (e))
            raise
        except ValueError as e:
            logger.error('ValueError %s' % (e))
            raise
        except Exception as e:
            logger.exception('%s' % (e))
            raise

def env_name():
    """ Return "Dev" or "Prod" depending on the name of folder the file is in /home/pi{Dev|Prod} 
    """
    filepath = os.path.abspath(__file__) # /home/pi/Dev/home_alarm/src/utils/this_file.py
    env      = filepath.split("/")[3]    # Dev / Prod
    return (env)
    