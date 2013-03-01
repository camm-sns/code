#!/usr/bin/env python
"""
    Optimization driver for Dakota
    It starts an ActiveMQ connection, sends it
    the new parameters and waits for completion.
"""
import sys
import os
from amq_kepler import dakota_client

# Get the parameter input file path
input_file = os.path.join(os.getcwd(), sys.argv[1])

# Get the results output file path
output_file = os.path.join(os.getcwd(), sys.argv[2])

# Set up a Dakota client
dakota = dakota_client.setup_client()

# Send the ActiveMQ message announcing new parameters
dakota.params_ready(input_file, output_file)

# Listen and wait for the results
dakota.listen_and_wait()

