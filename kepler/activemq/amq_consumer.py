"""
    Base ActiveMQ consumer class
"""
import time
import stomp
import logging

class Consumer(stomp.ConnectionListener):

    def __init__(self, brokers, user, passcode, 
                 queues=None, consumer_name="amq_consumer"):
        """ 
            @param brokers: list of brokers we can connect to
            @param user: activemq user
            @param passcode: passcode for activemq user
            @param queues: list of queues to listen to
            @param consumer_name: name of the AMQ listener
        """
        self._brokers = brokers
        self._user = user
        self._passcode = passcode
        ## Delay between loops
        self._delay = 5.0
        self._connection = None
        self._connected = False        
        self._queues = queues
        self._consumer_name = consumer_name
        
    def on_message(self, headers, message):
        """
            Process a message.
            @param headers: message headers
            @param message: JSON-encoded message content
        """
        # Acknowledge message
        # self._connection.ack(headers)
        print message
        
    def on_disconnected(self):
        self._connected = False
        
    def connect(self):
        """
            Connect to a broker
        """
        # Do a clean disconnect first
        self._disconnect()
        
        conn = stomp.Connection(host_and_ports=self._brokers, 
                                user=self._user,
                                passcode=self._passcode, 
                                wait_on_receipt=True)
        conn.set_listener(self._consumer_name, self)
        conn.start()
        conn.connect()
        for q in self._queues:
            conn.subscribe(destination=q, ack='auto', persistent='true')
        self._connection = conn
        self._connected = True
        logging.info("Connected to %s:%d\n" % conn.get_host_and_port())
    
    def _disconnect(self):
        """
            Clean disconnect
        """
        if self._connection is not None and self._connection.is_connected():
            self._connection.disconnect()
        self._connection = None
        
    def listen_and_wait(self, waiting_period=1.0):
        """
            Listen for the next message from the brokers.
            This method will simply return once the connection is
            terminated.
            @param waiting_period: sleep time between connection to a broker
        """
        self.connect()
        while(self._connected):
            time.sleep(waiting_period)
    
    def processing_loop(self):
        """
            Process events as they happen. A new listening connection
            will be established once the current connection is terminated.
        """
        listen = True 
        while(listen):
            try:
                # Wait for the next message
                self.listen_and_wait(self._delay)
            except KeyboardInterrupt:
                listen = False
            finally:
                self._disconnect()
