'''
Produce a resolution function

Create on Apr 8, 2013

@author: jmborr
'''

if __name__ == "__main__":
  import argparse
  import sys
  from sets import Set
  p=argparse.ArgumentParser(description='Provider for services involving the production of a resolution function. Available services are: None')
  p.add_argument('service', help='name of the service to invoke')
  p.add_argument('-explain', action='store_true', help='print message explaining the arguments to pass for the particular service')
  if Set(['-h', '-help', '--help']).intersection(Set(sys.argv)): args=p.parse_args() # check if help message is requested
