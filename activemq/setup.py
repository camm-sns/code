"""
    Install the ActiveMQ module for Kepler
    
    Requires stomp.py: run easy_install stomp.py
    
    Installs the kepler_consumer script, which can be called
    to start an ActiveMQ consumer for Kepler
    
"""
from setuptools import setup
import shutil

setup(
    name         = "amq_kepler",
    version      = "1.0",
    description  = "ActiveMQ consumer for Kepler",
    author       = "Oak Ridge National Laboratory",
    package_dir  = {'amq_kepler': '.'},
    packages     = ['amq_kepler'],
    entry_points = {'console_scripts':["kepler_client = amq_kepler.kepler_client:run",
                                       "dakota_client = amq_kepler.dakota_client:run",]},
    )   
