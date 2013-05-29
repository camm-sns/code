#!/usr/bin/env python
"""
    ActiveMQ service for Kepler
"""
import os
import sys
import json
import logging
import subprocess

from sns_utilities.amq_connector.amq_consumer import Client, Listener
from sns_utilities.amq_connector import listener_daemon
from configuration import Configuration


class KeplerConfiguration(Configuration):
    """
        Kepler client configuration.
        Adds the parameter_ready queue to the list of queues
        to subscribe to.
    """
    def __init__(self, config_file=None):
        super(KeplerConfiguration, self).__init__(config_file)
        self.queues = [self.params_ready_queue]

    
class KeplerListener(Listener):
    """
        ActiveMQ listener implementation for a Kepler client.
    """
    
    def __init__(self, configuration=None):
        super(KeplerListener, self).__init__(configuration)
        if configuration is not None:
            self.params_ready_queue = configuration.params_ready_queue
            self.default_results_ready_queue = configuration.results_ready_queue
            self.kepler_executable = configuration.kepler_executable
        
        logging.info("Kepler executable: %s" % self.kepler_executable)

    def on_message(self, headers, message):
        """
            Process a message.
            @param headers: message headers
            @param message: JSON-encoded message content
        """
        if headers['destination']=='/queue/'+self.params_ready_queue:
            
            # Decode the incoming message
            try:
                data_dict = json.loads(message)
            except:
                logging.error("Could not process JSON message")
                logging.error(str(sys.exc_value))

            # Start a Kepler job in a separate thread
            # The Kepler job will send an AMQ message to the given
            # queue upon completion
            if 'amq_results_queue' in data_dict:
                result_queue = data_dict['amq_results_queue']
            result_queue = self.default_results_ready_queue
            
            try:
                logging.info("Rcv: %s | Result queue: %s" % (self.params_ready_queue, result_queue))
                subprocess.Popen([self.kepler_executable, '-q', result_queue])
            except:
                logging.error("Could not launch Kepler job")
                logging.error(str(sys.exc_value))

def run():
    """
        Run an instance of the Kepler ActiveMQ consumer
    """
    listener_daemon.run(configuration_cls=KeplerConfiguration, 
                        listener_cls=KeplerListener, 
                        default_conf='/etc/kepler_consumer.conf')

if __name__ == "__main__": 
    run()