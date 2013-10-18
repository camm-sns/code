'''
Convolve the simulated S(Q,E) with a model beamline

Created on Mar 19, 2013

@author: jmborr
'''
from pdb import set_trace as trace # uncomment only for debugging purposes

def getParams(paramsFile):
  """Load the params file from Dakota onto a standard dictionary"""
  from itertools import islice
  import re
  pf=open(paramsFile)
  # find number of parameters to read
  nparm=int( re.compile('(\d+)\s+variable').search(pf.readline()).group(1) )
  # initialize dictionary containing values for the parameters
  parms={}
  for line in islice(pf,nparm):
    val,name=line.split()
    parms[name]=float(val)
  pf.close()
  return parms

def camm_convolve(signal,response,mode='same'):
  """In-house convolution

  Does a convolution according to the following definition:
                     (f*g)(t) = \integral_{f(t')*g(t'-t)*dt'}
  This definition is that of standard mathematical texts, except for g(t'-t) which in 
  standard mathematical texts is g(t-t'). This implies we have to reverse the input
  response function if we are to use any mathematical library, such as numpy.convolve
  
  Arguments:
    signal: numpy array corresponding to the signal
    response: numpy array corresponding to the response function that we slide along the t' axis
    [mode]: string indicating the mode for argument 'mode' of numpy.convolve. See numpy.convolve
            for details on the meaning of mode.

  Returns
    in-house convolution of signal and response
  """
  from numpy import convolve
  g=response[::-1] # numpy convolve uses the definition of convolution of math textbooks, which does E --> -E
  return convolve(signal,g,mode=mode)

def convolution(simulated, resolution, expdata, convolved, dak=None, norm2one=False):
  """Convolve a simulated S(Q,E) with a resolution file

  Arguments:
    simulated: Nexus file containing S(Q,E) from a simulation
    resolution: Nexus file containing the resolution. This will be used to produce a elastic line.
    convolved: Output Nexus file containing the convolution of the simulated S(Q,E) with the model beamline.
    expdata: Optional, experimental nexus file. Convolved will be binned as expdata. 
  Returns:
    workspace for the convolution
  """
  from mantid.simpleapi import (LoadNexus, Rebin, ConvertToHistogram, NormaliseToUnity, SaveNexus, SaveAscii, AddSampleLog)
  wss=LoadNexus(Filename=simulated,OutputWorkspace='simulated')
  width=wss.readX(0)[1]-wss.readX(0)[0] # rebin resolution as simulated
  wsr=LoadNexus(Filename=resolution,OutputWorkspace='resolution')

  #symmetrize the domain of the resolution function. Otherwise the
  #convolution results in a function with its peak shifted from the origin
  min=wsr.readX(0)[0]
  max=wsr.readX(0)[-1]
  delta=min+max
  if delta<0:
    wsr=Rebin(wsr, Params=(-max,width,max))
  elif delta>0:
    wsr=Rebin(wsr, Params=(min,width,-min))
  else:
    wsr=Rebin(wsr, Params=(min,width,max))

  # convolve now, overwriting simulateds
  for i in range(wss.getNumberHistograms()):
    v=wsr.readY(i)
    w=wss.readY(i)
    x=camm_convolve(w,v,mode='same')
    wss.setY(i,x)
    
  wse=LoadNexus(Filename=expdata,OutputWorkspace='expdata')
  width=wse.readX(0)[1]-wse.readX(0)[0] # rebin simulated as expdata
  Rebin(InputWorkspace='simulated', Params=(wse.readX(0)[0],width,wse.readX(0)[-1]), OutputWorkspace='convolved')
  ConvertToHistogram(InputWorkspace='convolved', OutputWorkspace='convolved') # remember that output from sassena are point-data
  if norm2one:
    wsc=NormaliseToUnity(InputWorkspace='convolved', OutputWorkspace='convolved')
  AddSampleLog(Workspace='convolved',LogName='NormaliseToUnity',LogText=str(float(norm2one)),LogType='Number')
  if dak:
    if convolved.endswith('b.nxs'):
      deriv=0.99
      dakota_vals = getParams(dak.rstrip('b')) # read in Dakota params file
    elif convolved.endswith('f.nxs'):
      deriv=1.01
      dakota_vals = getParams(dak.rstrip('f')) # read in Dakota params file
    else:
      deriv=1.0
      dakota_vals = getParams(dak) # read in Dakota params file
    AddSampleLog(Workspace='convolved',LogName='FF1',LogText=str(deriv*dakota_vals["FF1"]),LogType='Number')
  from mantid.simpleapi import mtd
  SaveNexus(InputWorkspace='convolved', Filename=convolved)
  return

if __name__ == "__main__":
  import argparse
  import sys
  if sys.version_info < (2,6): from sets import Set as set
  p=argparse.ArgumentParser(description='Provider for services involving convolution of simulated S(Q,E) with a model beamline. Available services are: lowTresolution.')
  p.add_argument('service', help='name of the service to invoke')
  p.add_argument('-explain', action='store_true', help='print message explaining the arguments to pass for the particular service')
  if Set(['-h', '-help', '--help']).intersection(Set(sys.argv)): args=p.parse_args() # check if help message is requested
  if 'convolution' in sys.argv:
    p.description='Convolve simulated S(Q,E) with a resolution Nexus file. Generates a Nexus file containing the convolution.' # update help message
    for action in p._actions:
      if action.dest=='service': action.help='substitue "service" with "convolution"' # update help message
    p.add_argument('--simulated', help='name of the nexus file containing the simulated S(Q,E)')
    p.add_argument('--resolution',help='name of the nexus file containing the resolution function. This will be used to produce an elastic line.')
    p.add_argument('--convolved', help='name of the output nexus file')
    p.add_argument('--expdata',   help='name of the experimental nexus file. Convolved will be binned as expdata.')
    p.add_argument('--dak',       help='name of the dakota params file')
    p.add_argument('--norm2one',  help='apply Mantid::NormaliseToUnity. Default is false')
    if '-explain' in sys.argv:
      p.parse_args(args=('-h',))
    else:
      args=p.parse_args()
      norm2one=False
      if args.norm2one in ('True','true','1'): norm2one=True
      convolution(args.simulated, args.resolution, args.expdata, args.convolved, dak=args.dak, norm2one=norm2one)
