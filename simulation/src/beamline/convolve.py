'''
Convolve the simulated S(Q,E) with a model beamline

Created on Mar 19, 2013

@author: jmborr
'''
from pdb import set_trace as trace # uncomment only for debugging purposes

def convolution(simulated, resolution, expdata, convolved):
  """Convolve a simulated S(Q,E) with a resolution file

  Arguments:
    simulated: Nexus file containing S(Q,E) from a simulation
    resolution: Nexus file containing the resolution. This will be used to produce a elastic line.
    convolved: Output Nexus file containing the convolution of the simulated S(Q,E) with the model beamline.
    expdata: Optional, experimental nexus file. Convolved will be binned as expdata. 
  Returns:
    workspace for the convolution
  """
  from mantid.simpleapi import (LoadNexus, Rebin, NormaliseToUnity, SaveNexus)
  from numpy import convolve
  wss=LoadNexus(Filename=simulated,OutputWorkspace='simulated')
  width=wss.readX(0)[1]-wss.readX(0)[0] # rebin resolution as simulated
  wsr=LoadNexus(Filename=resolution,OutputWorkspace='resolution')
  wsr=Rebin(InputWorkspace='resolution', Params=(wsr.readX(0)[0], width, wsr.readX(0)[-1]), OutputWorkspace='resolution')
  # convolve now, overwriting simulateds
  for i in range(wss.getNumberHistograms()):
    v=wsr.readY(i)
    w=wss.readY(i)
    x=convolve(v,w,mode='same') # CRITICAL: assumed X-array of simulateds > X-array of convolution
    wss.setY(i,x)
  wse=LoadNexus(Filename=expdata,OutputWorkspace='expdata')
  width=wse.readX(0)[1]-wse.readX(0)[0] # rebin simulated as expdata
  Rebin(InputWorkspace='simulated', Params=(wse.readX(0)[0],width,wse.readX(0)[-1]), OutputWorkspace='simulated')
  wsc=NormaliseToUnity(InputWorkspace='simulated', OutputWorkspace='convolved')
  #trace()
  SaveNexus(InputWorkspace='convolved', Filename=convolved)
  return wsc

if __name__ == "__main__":
  import argparse
  import sys
  from sets import Set
  p=argparse.ArgumentParser(description='Provider for services involving convolution of simulated S(Q,E) with a model beamline. Available services are: lowTresolution.')
  p.add_argument('service', help='name of the service to invoke')
  p.add_argument('-explain', action='store_true', help='print message explaining the arguments to pass for the particular service')
  if Set(['-h', '-help', '--help']).intersection(Set(sys.argv)): args=p.parse_args() # check if help message is requested
  if 'convolution' in sys.argv:
    p.description='Convolve simulated S(Q,E) with a resolution Nexus file. Generates a Nexus file containing the convolution.' # update help message
    for action in p._actions:
      if action.dest=='service': action.help='substitue "service" with "convolution"' # update help message
    p.add_argument('--simulated',help='name of the nexus file containing the simulated S(Q,E)')
    p.add_argument('--resolution',help='name of the nexus file containing the resolution function. This will be used to produce an elastic line.')
    p.add_argument('--convolved',help='name of the output nexus file')
    p.add_argument('--expdata',help='name of the experimental nexus file. Convolved will be binned as expdata.')
    if '-explain' in sys.argv:
      p.parse_args(args=('-h',))
    else:
      args=p.parse_args()
      convolution(args.simulated, args.resolution, args.expdata, args.convolved)
