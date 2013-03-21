'''
Created on Mar 20, 2013

@author: jmborr
'''

def parse_results(r):
  """Parse the results returned by evaluation of the Fit algoritm
  
  Arguments:
    r: python object returned by evaluation of the Fit algorithm
    
  Returns:
    Dictionary containing different values of interests. The dictionary contents are:
    
  """
  parsed={'OutputStatus':r[0],
          'OutputChi2overDoF':r[1]
          }
  return parsed
