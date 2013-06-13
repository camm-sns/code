#!/usr/bin/env python
"""
    Dummy AMQ producer to test the Kepler service
"""
import json
import argparse
import os
from sns_utilities.amq_connector.amq_consumer import Client
from camm_amq.configuration import Configuration
import time

# Setup the AMQ client
conf = Configuration('/etc/kepler_consumer.conf')
c = Client(conf.brokers, conf.amq_user, conf.amq_pwd)

# Parse command arguments
parser = argparse.ArgumentParser(description='Dummy Kepler workflow')
parser.add_argument(conf.kepler_result_queue_flag, metavar='return_queue',
                    default='DAKOTA.RESULTS.TEST',
                    help='AMQ queue to send results to',
                    dest='return_queue')
parser.add_argument(conf.kepler_output_file_flag, metavar='output_file',
                    default='results.out',
                    help='Kepler output file',
                    dest='output_file')
namespace = parser.parse_args()

output_file = namespace.output_file
value = output_file.split(".")[-1]

# Send a simple message to the return queue
message = {'params': 'test',
           'output_file': output_file,
           'cost_function': value
           }
json_message = json.dumps(message)
c.send(destination='/queue/'+namespace.return_queue, message=json_message)
c._disconnect()
