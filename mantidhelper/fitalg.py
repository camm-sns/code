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
  from mantid.simpleapi import ExtractSingleSpectrum
  prefix=r[4].getName()
  return {'message status':r[0],
          'Cost':r[1],
          'NormalisedCovarianceMatrix':r[2],
          'Parameters':r[3],
          'Workspace':r[4],
          'Data':ExtractSingleSpectrum(r[4],OutputWorkspace=prefix+'_Data',WorkspaceIndex=0),
          'Calc':ExtractSingleSpectrum(r[4],OutputWorkspace=prefix+'_Calc',WorkspaceIndex=1),
          'Diff':ExtractSingleSpectrum(r[4],OutputWorkspace=prefix+'_Diff',WorkspaceIndex=2),
          }
