#!/usr/bin/env python
"""
    Dummy AMQ producer to test the Kepler service
"""
import json
import argparse
from sns_utilities.amq_connector.amq_consumer import Client
from camm_amq.configuration import Configuration

# Parse command arguments
parser = argparse.ArgumentParser(description='Dummy Kepler workflow')
parser.add_argument('-q', metavar='return_queue',
                    default='DAKOTA.RESULTS.TEST',
                    help='AMQ queue to send results to',
                    dest='return_queue')
namespace = parser.parse_args()

# Setup the AMQ client
conf = Configuration('/etc/kepler_consumer.conf')
c = Client(conf.brokers, conf.amq_user, conf.amq_pwd)

# Send a simple message to the return queue
message = {'params': 'test'}
json_message = json.dumps(message)
c.send(destination='/queue/'+namespace.return_queue, message=json_message)
c._disconnect()
