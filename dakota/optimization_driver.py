#!/usr/bin/env python
"""
    Optimization driver for Dakota
    It starts an ActiveMQ connection, sends it
    the new parameters and waits for completion.
"""
import sys
import os
from camm_amq import dakota_client
#from camm_amq.camm_monitor import send_status_info

# Get the parameter input file path
input_file = os.path.join(os.getcwd(), sys.argv[1])

# Get the results output file path
output_file = os.path.join(os.getcwd(), sys.argv[2])

# Get parent PID so we have a unique instance number
# for the Dakota process
instance_number = sys.argv[3]

# Get the working directory
working_directory = os.path.dirname(os.path.abspath(__file__))

# Set up a Dakota client
dakota = dakota_client.setup_client(instance_number, working_directory)

# Send the ActiveMQ message announcing new parameters
dakota.params_ready(input_file, output_file)
#send_status_info(str(instance_number), 'dakota_start')

# Listen and wait for the results
dakota.listen_and_wait()
#send_status_info(str(instance_number), 'dakota_stop')
