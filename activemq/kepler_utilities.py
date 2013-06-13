#!/usr/bin/env python
"""
    ActiveMQ client for Dakota
"""
import os
import sys
import json
import logging
import argparse
import threading
import time

# Set log level set up log file handler
logging.getLogger().setLevel(logging.INFO)
ft = logging.Formatter('%(asctime)-15s %(message)s')
fh = logging.FileHandler('kepler_job.log')
fh.setLevel(logging.INFO)
fh.setFormatter(ft)
logging.getLogger().addHandler(fh)

from sns_utilities.amq_connector.amq_consumer import Client, Listener
from configuration import Configuration

class KeplerJobListener(Listener):
    """
        ActiveMQ Listener for Kepler
        This class processes incoming messages
    """
    
    def __init__(self, params_ready_queue):
        super(KeplerJobListener, self).__init__()
        
        self._complete = False
        self._transaction_complete = threading.Condition()
        self.params_ready_queue = params_ready_queue

    def on_message(self, headers, message):
        """
            Process a message.
            @param headers: message headers
            @param message: JSON-encoded message content
        """
        if headers['destination']=='/queue/'+self.params_ready_queue:
            logging.info("Rcv: %s" % headers['destination'])
            try:               
                self._transaction_complete.acquire()
                self._complete = True
                self._transaction_complete.notify()
                self._transaction_complete.release()
            except:
                logging.error("Could not process JSON message")
                logging.error(str(sys.exc_value))

    def wait_on_transaction_complete(self):
        """
            Wait for the results ready message
        """
        logging.info("Waiting for message")
        self._transaction_complete.acquire()
        while not self._complete == True:
            logging.info("Message received")
            self._transaction_complete.wait()
        self._transaction_complete.release()         
        
        
class KeplerJobClient(Client):
    """
        ActiveMQ Client for Dakota
        This class hold the connection to ActiveMQ and 
        starts the listening thread.
    """
    ## Input queue used to trigger a new calculation
    PARAMS_READY_QUEUE = "PARAMS.READY"
        
    def set_params_ready_queue(self, queue):
        """ 
            Set the name of the queue to be used to 
            request new calculations/simulations
            @param queue: name of an ActiveMQ queue
        """
        self.PARAMS_READY_QUEUE = queue
        
    def listen_and_wait(self, waiting_period=1.0):
        """
            Listen for the next message from the brokers.
            @param waiting_period: sleep time between connection to a broker
        """       
        listening = True
        while(listening):
            try:
                if self._connection is None or self._connection.is_connected() is False:
                    self.connect()                
                time.sleep(waiting_period)
                
                # Wait for the listening thread to receive the results message
                self._listener.wait_on_transaction_complete()
                
                # Once the results message has been received and dealt with,
                # we can simply stop listening
                logging.info("Unsubscribing to %s" % self.PARAMS_READY_QUEUE)
                self._connection.unsubscribe(destination=self.PARAMS_READY_QUEUE)
                if self._connection.get_listener(self._consumer_name) is not None:
                    logging.info("Removing listener %s" % self._consumer_name)
                    self._connection.remove_listener(self._consumer_name)
                self._connection.stop()
                listening = False
            
            # Catch Ctrl-C for interactive running
            except KeyboardInterrupt:
                sys.exit(0)
            except:
                logging.error("Problem connecting to AMQ broker")
                logging.error("%s: %s" % (sys.exc_type,sys.exc_value))
                time.sleep(5.0)


def setup_client(instance_number,
                 config_file='/etc/kepler_consumer.conf'):
    """
        Create an instance of the Kepler job ActiveMQ consumer
        @param instance_number: instance number to use for 
                                transient process communication
        @param config_file: configuration file to use to setup the client
    """ 
    # Look for configuration
    conf = Configuration(config_file)

    params_queue = "%s.%s" % (conf.params_ready_queue, str(instance_number))
    
    # Parse command arguments
    parser = argparse.ArgumentParser(description='Dummy Kepler workflow')
    parser.add_argument(conf.kepler_params_queue_flag, metavar='params_queue',
                        default=params_queue,
                        help='AMQ queue to receive new parameters from ',
                        dest='params_queue')    
    namespace = parser.parse_args()
    
    queues = [namespace.params_queue]
    c = KeplerJobClient(conf.brokers, conf.amq_user, conf.amq_pwd, 
                     queues, "dakota_consumer")
    c.set_params_ready_queue(params_queue)
    c.set_listener(KeplerJobListener(params_queue))
    return c
 
if __name__ == "__main__":
    c=setup_client(os.getpid())
    c.listen_and_wait()