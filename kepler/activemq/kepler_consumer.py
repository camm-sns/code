#!/usr/bin/env python
"""
    Start an ActiveMQ consumer
"""
import os
import json
from amq_consumer import Consumer

class KeplerConsumer(Consumer):
    
    def __init__(self, brokers, user, passcode, 
                 queues=None, consumer_name="amq_consumer"):
        super(KeplerConsumer, self).__init__(brokers, user, passcode, 
                                             queues, consumer_name)
        
    def on_message(self, headers, message):
        """
            Process a message.
            @param headers: message headers
            @param message: JSON-encoded message content
        """
        fd = open("/Users/m2d/kepler.out", 'a')
        fd.write(message+'\n')
        fd.close()

def run(consumer=KeplerConsumer):
    """
        Run an instance of the Kepler ActiveMQ consumer
        
        @param consumer: Consumer class
    """
    # Dummy ActiveMQ settings for testing
    amq_user = 'icat'
    amq_pwd  = 'icat'
    brokers  = [('localhost', 61613)] 
    queues   = ['foo.bar']
    
    # Look for configuration
    if os.path.exists('/etc/kepler_consumer.conf'):
        cfg = open('/etc/kepler_consumer.conf', 'r')
        json_encoded = cfg.read()
        try:
            config = json.loads(json_encoded)
        
            if type(config)==dict:
                
                if config.has_key('amq_user'):
                    amq_user = config['amq_user']
                    
                if config.has_key('amq_pwd'):
                    amq_pwd = config['amq_pwd']
                
                if config.has_key('brokers'):
                    b_str = config['brokers']
                
                if config.has_key('queues'):
                    q_str = config['queues']
                    q_list = q_str.split(',')
                    queues = [q.strip() for q in q_list]
        except:
            print "Could not read configuration file:\n  %s" % str(sys.exc_value)
    
    c = consumer(brokers, amq_user, amq_pwd, queues, "Kepler_consumer")
    c.processing_loop()

if __name__ == "__main__": 
    run(consumer=KeplerConsumer)