#!/usr/bin/env python
"""
    ActiveMQ client for Dakota
"""
import os
import sys
import json
import logging
import argparse

# Set log level set up log file handler
logging.getLogger().setLevel(logging.INFO)
ft = logging.Formatter('%(asctime)-15s %(message)s')
fh = logging.FileHandler('dakota_client.log')
fh.setLevel(logging.INFO)
fh.setFormatter(ft)
logging.getLogger().addHandler(fh)

from sns_utilities.amq_connector.amq_consumer import Client, Listener
from configuration import Configuration

class DakotaListener(Listener):
    """
        ActiveMQ Listener for Dakota
        This class processes incoming messages
    """
    
    def __init__(self, configuration=None, results_ready_queue=None):
        super(DakotaListener, self).__init__(configuration)
        if results_ready_queue is not None:
            self.results_ready_queue = results_ready_queue
        else:
            configuration.results_ready_queue

    def on_message(self, headers, message):
        """
            Process a message.
            @param headers: message headers
            @param message: JSON-encoded message content
        """
        if headers['destination']=='/queue/'+self.results_ready_queue:
            
            try:
                data_dict = json.loads(message)
                output_file = data_dict['output_file']
                
                logging.info("Rcv: %s | Output file: %s" % (self.results_ready_queue, output_file))
                
                fd = open(output_file, 'w')
                fd.write('%f\n' % data_dict['cost_function'])
                fd.close()
            except:
                logging.error("Could not process JSON message")
                logging.error(str(sys.exc_value))

        
        
class DakotaClient(Client):
    """
        ActiveMQ Client for Dakota
        This class hold the connection to ActiveMQ and 
        starts the listening thread.
    """
    ## Input queue used to trigger a new calculation
    PARAMS_READY_QUEUE = "PARAMS.READY"
    ## Output queue to announce results
    RESULTS_READY_QUEUE = "RESULTS.READY"
    
    def set_results_ready_queue(self, queue):
        """ 
            Set the name of the queue to be used to 
            announce new results
            @param queue: name of an ActiveMQ queue
        """
        self.RESULTS_READY_QUEUE = queue
        
    def set_params_ready_queue(self, queue):
        """ 
            Set the name of the queue to be used to 
            request new calculations/simulations
            @param queue: name of an ActiveMQ queue
        """
        self.PARAMS_READY_QUEUE = queue
        
    def set_working_directory(self, working_directory):
        """
            Set the working directory in which Dakota will write
            @param working_directory: directory for dakota to write parameter files
        """
        self.working_directory = working_directory
        
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
                           'output_file': output_file,
                           'amq_results_queue': self.RESULTS_READY_QUEUE,
                           'working_directory': self.working_directory
                           }
                json_message = json.dumps(message)
                self.send(self.PARAMS_READY_QUEUE, json_message)
            except:
                logging.error("Could not read %s file: %s" % (input_file, sys.exc_value))
        else:
            logging.error("Parameter file %s does not exist" % input_file)


def setup_client(instance_number=None, 
                 working_directory=None, 
                 config_file='/etc/kepler_consumer.conf'):
    """
        Create an instance of the Dakota ActiveMQ consumer
        @param instance_number: instance number to use for 
                                transient process communication
        @param working_directory: directory for dakota to write parameter files
        @param config_file: configuration file to use to setup the client
    """
    # Make sure we have an instance number
    if instance_number is None:
        instance_number = os.getppid()
        
    # Determine the working directory
    if working_directory is None:
        working_directory = os.path.expanduser('~')
        
    # Look for configuration
    conf = Configuration(config_file)

    results_queue = "%s.%s" % (conf.results_ready_queue, str(instance_number))
    queues = [results_queue]
    c = DakotaClient(conf.brokers, conf.amq_user, conf.amq_pwd, 
                     queues, "dakota_consumer")
    c.set_params_ready_queue(conf.params_ready_queue)
    c.set_results_ready_queue(results_queue)
    c.set_working_directory(working_directory)
    c.set_listener(DakotaListener(conf, results_ready_queue=results_queue))
    return c
    
    
def run():
    """
        Run an instance of the Dakota ActiveMQ consumer
    """
    # Get the command line options
    parser = argparse.ArgumentParser(description='Dakota AMQ client')
    parser.add_argument('-c', metavar='configuration',
                        default='/etc/kepler_consumer.conf',
                        help='location of the configuration file',
                        dest='config_file')
    parser.add_argument('-d', metavar='work_directory',
                        default='/tmp',
                        help='location of the working directory',
                        dest='work_directory')
    parser.add_argument('-t',
                        action='store_true',
                        help='test execution',
                        dest='is_test')
    namespace = parser.parse_args()

    c = setup_client(working_directory=namespace.work_directory,
                     config_file=namespace.config_file)
    
    if namespace.is_test is True:
        fd = open(namespace.work_directory+'/test_params.in', 'w')
        fd.write("123.456")
        fd.close()
        c.params_ready(namespace.work_directory+'/test_params.in',
                       namespace.work_directory+'/test_results.out')

    c.listen_and_wait(0.1)

if __name__ == "__main__": 
    run()