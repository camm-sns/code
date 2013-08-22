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

from sns_utilities.amq_connector.amq_consumer import Client, Listener
from configuration import Configuration
from camm_monitor import send_status_info

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
        #send_status_info(str(os.getpid()), 'start_iteration')

        logging.info("Rcv: %s" % headers['destination'])
        if headers['destination']=='/queue/'+self.params_ready_queue:
            logging.info("  -Ready to exit")
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
 
 
def run_kepler_client():
    """
        Entry point for kepler_client console script.
        Starts an AMQ client for Kepler.
    """
    # Set log level set up log file handler
    logging.getLogger().setLevel(logging.ERROR)
    ft = logging.Formatter('%(asctime)-15s %(message)s')
    fh = logging.FileHandler('kepler_job.log')
    fh.setLevel(logging.ERROR)
    fh.setFormatter(ft)
    logging.getLogger().addHandler(fh)

    # Create a configuration object
    conf = Configuration()
    logging.error(str(sys.argv))
    parser = argparse.ArgumentParser(description='Kepler workflow client')
    parser.add_argument(conf.kepler_params_queue_flag, metavar='params_queue',
                        required=True,
                        help='AMQ queue to receive new parameters from ',
                        dest='params_queue')    
    namespace = parser.parse_args()

    params_queue = "%s.%s" % (conf.params_ready_queue, str(os.getpid()))

    logging.info("Parameter queue is %s" % namespace.params_queue)
    
    queues = [namespace.params_queue]
    c = KeplerJobClient(conf.brokers, conf.amq_user, conf.amq_pwd, 
                     queues, "kepler_consumer")
    c.set_params_ready_queue(namespace.params_queue)
    c.set_listener(KeplerJobListener(namespace.params_queue))
    send_status_info(str(os.getpid()), 'start_iteration')
    c.listen_and_wait()
    
        
def send_amq_results_ready():
    """
        Entry point for console script to send a results-ready message to AMQ
    """
    # Create a configuration object
    conf = Configuration()
    
    # Parse command arguments
    parser = argparse.ArgumentParser(description='Kepler workflow communication')
    parser.add_argument(conf.kepler_result_queue_flag, metavar='return_queue',
                        required=True,
                        help='AMQ queue to send results to',
                        dest='return_queue')
    parser.add_argument(conf.kepler_output_file_flag, metavar='output_file',
                        default='results.out',
                        help='Kepler output file',
                        dest='output_file')
    namespace = parser.parse_args()

    # Setup the AMQ client
    c = Client(conf.brokers, conf.amq_user, conf.amq_pwd)

    # Send a simple message to the return queue
    message = {'output_file': namespace.output_file}
    c.send(destination='/queue/'+namespace.return_queue, message=json.dumps(message))
    c._disconnect()

    send_status_info(str(os.getpid()), 'stop_iteration')

if __name__ == "__main__":
    run_kepler_client()
