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

# Set log level set up log file handler
logging.getLogger().setLevel(logging.INFO)
ft = logging.Formatter('%(asctime)-15s %(message)s')
fh = logging.FileHandler('/var/log/amq_listener_daemon.log')
fh.setLevel(logging.INFO)
fh.setFormatter(ft)
logging.getLogger().addHandler(fh)

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
            self.kepler_result_queue_flag = configuration.kepler_result_queue_flag
            self.kepler_work_dir_flag = configuration.kepler_work_dir_flag
            self.kepler_run_options = configuration.kepler_run_options
            self.kepler_workflow = configuration.kepler_workflow
            self.kepler_output_file_flag = configuration.kepler_output_file_flag
        
        logging.info("Kepler executable: %s | Found: %s" % (self.kepler_executable, str(os.path.isfile(self.kepler_executable))))        

    def _build_command(self, result_queue, work_directory, output_file):
        """
            Build the Kepler command
            @param result_queue: name of the AMQ queue to reply to once the Kepler is completed
            @param work_directory: Dakota work directory
            @param output_file: name of the results output file (example: results.out.2)
        """
        command = [self.kepler_executable,
                   "-runwf", self.kepler_workflow, "-nogui", 
                   self.kepler_result_queue_flag, result_queue,
                   self.kepler_work_dir_flag, work_directory,
                   self.kepler_output_file_flag, output_file]
        for item in self.kepler_run_options:
            command.append(item)
        return command
        
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
            else:
                result_queue = self.default_results_ready_queue
            
            if 'working_directory' in data_dict:
                working_directory = data_dict['working_directory']
            else:
                working_directory = '/tmp'
            
            if 'output_file' in data_dict:
                output_file = data_dict['output_file']
            else:
                output_file = 'results.out'
            
            try:
                logging.info("Rcv: %s | Result queue: %s" % (self.params_ready_queue, result_queue))
                command = self._build_command(result_queue, working_directory, output_file)
                logging.info("Kepler cmd: %s" % ' '.join(command))
                subprocess.Popen(command)
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
