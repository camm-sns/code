#!/usr/bin/env python
"""
    ActiveMQ client for Kepler
"""
import os
import sys
import json
import logging
from amq_consumer import Client, Configuration, Listener

# Set log level
logging.getLogger().setLevel(logging.INFO)
# Formatter
ft = logging.Formatter('%(asctime)-15s %(message)s')
# Create a log file handler
fh = logging.FileHandler('kepler.log')
fh.setLevel(logging.INFO)
fh.setFormatter(ft)
logging.getLogger().addHandler(fh)


class KeplerListener(Listener):
    """
        ActiveMQ listener implementation for a Kepler client.
    """
    ## Connection used for sending messages
    _send_connection = None
    
    def on_message(self, headers, message):
        """
            Process a message.
            @param headers: message headers
            @param message: JSON-encoded message content
        """
        if headers['destination']=='/queue/'+self.PARAMS_READY_QUEUE:
            
            # Decode the incoming message
            try:
                data_dict = json.loads(message)
            except:
                logging.error("Could not process JSON message")
                logging.error(str(sys.exc_value))

            # Evaluate the cost function and send back the 
            # result through ActiveMQ
            try:                        
                data_dict['cost_function'] = 124.0
                json_message = json.dumps(data_dict)
                
                # Establish an AMQ connection as needed before sending message
                if self._send_connection is None:
                    self._send_connection = self.configuration.get_client('keplerlistener')
                self._send_connection.send(data_dict['amq_results_queue'], json_message)                
            except:
                logging.error("Could not report back results")
                logging.error(str(sys.exc_value))                
        
        fd = open(os.path.join(os.path.expanduser('~'), "kepler.out"), 'a')
        fd.write(message+'\n')
        fd.close()

def run():
    """
        Run an instance of the Kepler ActiveMQ consumer
    """
    # Look for configuration
    conf = Configuration('/etc/kepler_consumer.conf')

    queues = conf.queues
    queues.append(conf.params_ready_queue)
    
    c = Client(conf.brokers, conf.amq_user, conf.amq_pwd, 
               queues, "kepler_consumer")
    c.set_listener(KeplerListener(conf))
    c.listen_and_wait(0.1)

if __name__ == "__main__": 
    run()