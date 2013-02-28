This directory is meant to contain Kepler-specific code and configuration for CAMM

# Pre-requisites
	 - stomp.py should be installed to enable ActiveMQ communication (http://code.google.com/p/stomppy/)
	 
# ActiveMQ Consumer Installation
	 - Run `python setup.py install` in the `activemq` directory.
	 
	 The setup.py script will not only install the amq_kepler module, but will
	 also create a script named `kepler_consumer` at a location where it can be
	 used by all users.
	 
	 In the event that the kepler_consumer script is not installed on the
	 system path, you can use the `--install-scripts` option when running 
	 the installation script:
	 
	 `python setup.py install --install-scripts /usr/local/bin`
	 
	 - To use the ActiveMQ consumer for Kepler, add an `External Execution` actor
	 to your workflow and execute `/usr/local/bin/kepler_consumer` with it.
	 
	 - The Kepler consumer can be configured by adding a file named
	 `kepler_consumer.conf` in /etc.
	 The configuration file should be in JSON format and can contain the
	 following parameters
	 
	 `
	 {
	    "brokers": [["localhost", 61613]], 
	 	"amq_queues": ["foo.bar"], 
	 	"amq_user": "icat",
	 	"amq_pwd": "icat"
	 }
	 `
	 