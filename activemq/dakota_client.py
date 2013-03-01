#!/usr/bin/env python
"""
    Start an ActiveMQ consumer for Dakota
"""
import os
import sys
import json
import logging
import threading
from amq_consumer import Client, Configuration, Listener

class DakotaListener(Listener):
    """
        ActiveMQ Listener for Dakota
        This class processes incoming messages
    """
    def on_message(self, headers, message):
        """
            Process a message.
            @param headers: message headers
            @param message: JSON-encoded message content
        """
        if headers['destination']=='/queue/'+self.RESULTS_READY_QUEUE:
            try:
                data_dict = json.loads(message)
                output_file = data_dict['output_file']
                fd = open(output_file, 'w')
                fd.write('%f\n' % data_dict['cost_function'])
                fd.close()
            except:
                logging.error("Could not process JSON message")
                logging.error(str(sys.exc_value))
            
        fd = open(os.path.join(os.path.expanduser('~'), "dakota.out"), 'a')
        fd.write(message+'\n')
        fd.close()
        self.connection.stop()
        
        
class DakotaClient(Client):
    """
        ActiveMQ Client for Dakota
        This class hold the connection to ActiveMQ and 
        starts the listening thread.
    """
    PARAMS_READY_QUEUE = "PARAMS.READY"
    
    def params_ready(self, input_file, output_file):
        """
            Send an ActiveMQ message announcing new
            parameters.
            @param input_file: parameters input file path
            @param output_file: results file to be created
        """
        if os.path.exists(input_file):
            try:
                fd = open(input_file, 'r')
                params = fd.read()
                message = {'params': params,
                           'output_file': output_file}
                json_message = json.dumps(message)
                self.send(self.PARAMS_READY_QUEUE, json_message)
            except:
                logging.error("Could not read %s file: %s" % (input_file, sys.exc_value))
        else:
            logging.error("Parameter file %s does not exist" % input_file)


def setup_client():
    """
        Create an instance of the Dakota ActiveMQ consumer
    """
    # Look for configuration
    conf = Configuration('/etc/kepler_consumer.conf')

    queues = [conf.results_ready_queue]
    c = DakotaClient(conf.brokers, conf.amq_user, conf.amq_pwd, 
                     queues, "Dakota_consumer")    
    c.set_listener(DakotaListener(conf, c))
    return c
    
    
def run():
    """
        Run an instance of the Dakota ActiveMQ consumer
    """
    c = setup_client()
    c.listen_and_wait(0.1)

if __name__ == "__main__": 
    run()