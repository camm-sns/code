import os
import sys
import json
import logging

from sns_utilities.amq_connector import configuration

class Configuration(configuration.Configuration):
    """
       Configuration class for CAMM 
    """
    params_ready_queue = 'PARAMS.READY'
    results_ready_queue = 'RESULTS.READY'
    kepler_executable = 'test/dummy_kepler_workflow.py'
    
    def __init__(self, config_file=None):
        super(Configuration, self).__init__(config_file)
        
        # Look for configuration
        if config_file is not None and os.path.exists(config_file):
            cfg = open(config_file, 'r')
            json_encoded = cfg.read()
            try:
                config = json.loads(json_encoded)
            
                if type(config)==dict:
                    if config.has_key('params_ready_queue'):
                        self.params_ready_queue = config['params_ready_queue']
                        
                    if config.has_key('results_ready_queue'):
                        self.results_ready_queue = config['results_ready_queue']
                        
                    if config.has_key('kepler_executable'):
                        self.kepler_executable = config['kepler_executable']
            except:
                logging.error("Could not read configuration file:\n  %s" % str(sys.exc_value))