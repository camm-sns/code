"""
    Install the ActiveMQ module for CAMM
    
    Requires stomp.py: run easy_install stomp.py
"""
from setuptools import setup
import shutil
import os
import sys
import site

setup(
    name         = "camm_amq",
    version      = "1.1",
    description  = "ActiveMQ consumer for CAMM",
    author       = "Oak Ridge National Laboratory",
    package_dir  = {'camm_amq': 'activemq'},
    packages     = ['camm_amq'],
    entry_points = {'console_scripts':["kepler_client = camm_amq.kepler_utilities:run_kepler_client",
                                       "kepler_results_ready = camm_amq.kepler_utilities:send_amq_results_ready",
                                       "dakota_client = camm_amq.dakota_client:run",
                                       "camm_status = camm_amq.camm_monitor:send_status_info_command",
                                       "camm_monitor = camm_amq.camm_monitor:run",]},
    )   
