"""
    Install the ActiveMQ module for CAMM
    
    Requires stomp.py: run easy_install stomp.py
"""
from setuptools import setup
import shutil

setup(
    name         = "camm_amq",
    version      = "1.0",
    description  = "ActiveMQ consumer for CAMM",
    author       = "Oak Ridge National Laboratory",
    package_dir  = {'camm_amq': '.'},
    packages     = ['camm_amq'],
    entry_points = {'console_scripts':["kepler_client = camm_amq.kepler_client:run",
                                       "dakota_client = camm_amq.dakota_client:run",]},
    )   
