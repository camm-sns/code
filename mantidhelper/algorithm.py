'''
Created on Mar 11, 2013

@author: jmborr
'''
#from pdb import set_trace as trace # uncomment only for debugging purposes

def toBool(value):
  """ returns False if passes either of the accepted false values. Otherwise returns True
  accepted false values are False', '0', 0, 'None', None, '()', (), '{}', {}
  """
  if value in ('False', '0', 0, 'None', None, '()', (), '{}', {}):
    return False
  return True

# Give correct type to algoritm arguments:
correct_type={'LoadSassena':{'TimeUnit':float,},
              'SassenaFFT':{'FTTonlyRealPart':int,'DetailedBalance':int,'Temp':float},
              'SaveNexus':{'Title':str}
              }

def correctAlgArgs(algname,thedict):
  """ Given a Mantid algorithm, correct the type of the arguments in 'thedict'

  Keywords of 'thedict' are algorithm properties, while values of 'thedict'
  are arguments for those properties, but with incorrect type. This can happen if
  we pass 'thedict' though the command line. Then arguments will all be strings

  Args:
    algname: name of the algorithm
    thedict: python dictionary containing property names and values for those properties

  Returns:
    'thedict' with values for the properties having the correct types

  Example:
    correctAlgArgs('LoadSassena',{'TimeUnit':'0.1'}) will turn '0.1' into float and
    return {'TimeUnit':'0.1'}
  """
  mapping={}
  if algname in correct_type.keys(): mapping=correct_type[algname]
  for key in thedict.keys():
    if key in mapping.keys(): thedict[key]=mapping[key](thedict[key])
  return thedict

def getDictFromArgparse(algname,arguments):
  """ Produce python dictionary of (property,value) pairs for a Mantid algorithm
  
  'arguments' is a argparse.Namespace object containing a string the defines
  (property,value) pairs for Mantid algorithm 'algname'. This function parses the
  string and returns the dictionary

  Args:
    algname: name of the Mantid algorithm
    arguments: argparse.Namespace object. Should contain attribute algname with value
      a string of (property,value) pairs in the follwing format:
      "prop1:val1,prop2:val2"

  Example:
    getDictFromArgparse('LoadSassena',arguments) where arguments.Loadsassena="TimeUnit:0.1"
    will return dictionary {TimeUnit:0.1}

  Returns:
    dictionary of (property,value) pairs that can be passed onto the Mantid
    algoritm 'algname'
  """
  thestring=arguments.__getattribute__(algname)
  thedict={}
  if thestring: thedict=dict( map( lambda x: x.split(':'), thestring.split(',') ) )
  return correctAlgArgs(algname,thedict)