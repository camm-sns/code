'''
Created on Mar 20, 2013

@author: jmborr
'''
from pdb import set_trace as trace # uncomment only for debugging purposes

def prunespectra(InputWorkspace=None,indexes=[]):
  """remove from InputWorkspace spectra with indexes in list indexes"""
  if not InputWorkspace or not indexes:
    return 0 # do nothing
  from mantid.simpleapi import (ExtractSingleSpectrum, AppendSpectra, RenameWorkspace)
  wst=None
  for index in indexes:
    if not wst:
      wst='prunespectra_temp'
      ExtractSingleSpectrum(InputWorkspace=InputWorkspace, OutputWorkspace=wst, WorkspaceIndex=index)
    else:
      wst2='prunespectra_temp2'
      ExtractSingleSpectrum(InputWorkspace=InputWorkspace, OutputWorkspace=wst2, WorkspaceIndex=index)
      AppendSpectra(InputWorkspace1=wst, InputWorkspace2=wst2, OutputWorkspace=wst)
  RenameWorkspace(InputWorkspace=wst, OutputWorkspace=InputWorkspace) # overwrite
  return len(indexes)