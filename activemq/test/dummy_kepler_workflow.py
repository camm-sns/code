#!/usr/bin/env python
"""
    Dummy AMQ producer to test the Kepler service
"""
import json
import argparse
from sns_utilities.amq_connector.amq_consumer import Client
from camm_amq.configuration import Configuration

# Setup the AMQ client
conf = Configuration('/etc/kepler_consumer.conf')
c = Client(conf.brokers, conf.amq_user, conf.amq_pwd)

# Parse command arguments
parser = argparse.ArgumentParser(description='Dummy Kepler workflow')
parser.add_argument(conf.kepler_result_queue_flag, metavar='return_queue',
                    default='DAKOTA.RESULTS.TEST',
                    help='AMQ queue to send results to',
                    dest='return_queue')
parser.add_argument(conf.kepler_work_dir_flag, metavar='working_dir',
                    default='/tmp',
                    help='Dakota working directory',
                    dest='working_dir')
parser.add_argument('-runwf', metavar='workflow',
                    default='Strategist.xml',
                    help='Kepler workflow',
                    dest='workflow')
namespace = parser.parse_args()

# Send a simple message to the return queue
message = {'params': 'test',
           'output_file': namespace.working_dir+'/dakota_test.out',
           'cost_function': 123.456
           }
json_message = json.dumps(message)
c.send(destination='/queue/'+namespace.return_queue, message=json_message)
c._disconnect()
