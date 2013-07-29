"""
    Reports current status of CAMM jobs
"""
import getpass
import time
import json
import argparse
import sys

from sns_utilities.amq_connector.amq_consumer import Client, Listener
from sns_utilities.daemon import Daemon
from configuration import Configuration

import logging

# Set log level set up log file handler
logging.getLogger().setLevel(logging.INFO)
ft = logging.Formatter('%(asctime)-15s %(message)s')
fh = logging.FileHandler('camm_listener.log')
fh.setLevel(logging.INFO)
fh.setFormatter(ft)
logging.getLogger().addHandler(fh)

def send_status_info_command():
    """
        Entry point for console script to send status information to AMQ
    """
    # Parse command arguments
    parser = argparse.ArgumentParser(description='Dakota process communication')
    parser.add_argument('-p', metavar='instance_number',
                        required=True,
                        help='Process identifier',
                        dest='instance_number')
    subparsers = parser.add_subparsers(dest='status', help='Available status messages')
    subparsers.add_parser('dakota_start',    help='Start a Dakota job')
    subparsers.add_parser('start_iteration', help='Start an iteration')
    subparsers.add_parser('stop_iteration',  help='Stop an iteration')
    subparsers.add_parser('dakota_stop',     help='Stop a Dakota job')
    namespace = parser.parse_args()
    
    send_status_info(namespace.instance_number, namespace.status)

    
def send_status_info(instance_number, status, code=0):
    """
        Send a status message to ActiveMQ
        @param instrance_numer: unique number of the CAMM job this process belongs to
        @param status: status string
        @param code: status code
    """
    try:
        int(instance_number)
    except:
        logging.error("Instance_number must be an integer. Found: %s" % str(instance_number))
        
    if status not in ['dakota_start', 'start_iteration', 'stop_iteration', 'dakota_stop']:
        logging.error("Invalid status string. Found: %s" % str(status))
        
    # Create a configuration object
    conf = Configuration()
    # Setup the AMQ client
    c = Client(conf.brokers, conf.amq_user, conf.amq_pwd)

    # Send a simple message to the return queue
    message = {'instance_number': instance_number,
               'user': str(getpass.getuser()),
               'timestamp': time.time(),
               'status': status,
               'code': code}
    
    c.send(destination='/topic/SNS.CAMM.STATUS.JOBS', message=json.dumps(message))
    c._disconnect()       
        
    
class CammListener(Listener):
    """
        CAMM listener
    """
    def on_message(self, headers, message):
        """
            Process a message.
            @param headers: message headers
            @param message: JSON-encoded message content
        """
        try:
            data_dict = json.loads(message)
            # Write status to DB
            logging.error(str(data_dict))
        except:
            logging.error("Problem processing message: %s" % sys.exc_value)
    

class ListenerDaemon(Daemon):
    """
        Listener daemon for CAMM framework.
        Listens to status messages sent from various processes.
    """
    def run(self):
        """
            Run the CAMM listener daemon
        """
        # Create a configuration object
        conf = Configuration()
        # Setup the AMQ client
        c = Client(conf.brokers, conf.amq_user, conf.amq_pwd, 
                   queues=['/topic/SNS.CAMM.STATUS.JOBS'])
        listener = CammListener(conf)
        c.set_listener(listener)
        c.listen_and_wait(0.1)
        

def run():
    """
        Console script entry point
    """
    parser = argparse.ArgumentParser(description='CAMM listener')
    subparsers = parser.add_subparsers(dest='command', help='available sub-commands')
    subparsers.add_parser('start', help='Start daemon [-h for help]')
    subparsers.add_parser('restart', help='Restart daemon [-h for help]')
    subparsers.add_parser('stop', help='Stop daemon')
    namespace = parser.parse_args()
    
    # Start the daemon
    daemon = ListenerDaemon('/tmp/camm_listener.pid',
                            stdout=None,
                            stderr=None)
        
    if namespace.command == 'start':
        daemon.start()
    elif namespace.command == 'stop':
        daemon.stop()
    elif namespace.command == 'restart':
        daemon.restart()

    sys.exit(0)
    
if __name__ == "__main__": 
    run()
