'''
Convolve the simulated S(Q,E) with a model beamline

Created on Mar 19, 2013

@author: jmborr
'''
from pdb import set_trace as trace # uncomment only for debugging purposes

def modelBEC(model, resolution, convolved, qvalues, assembled):
  """Assemble the Background, Elastic line and Convolution of the resolution with the simulated S(Q,E)
  This is a hard-coded model consisting of a linear background, and elastic line, and a convolution:
    b0+b1*E  +  e0*exp(-e1*Q^2)*Elastic(E)  +  c0*Resolution(E)xSimulated(Q,E)
    We load Resolution(E)xSimulated(Q,E) as Convolved(Q,E)
    
  Arguments:
    model: beamline model file is a single line, e.g,
           b0=1.3211; b1=0.00 e0=0.99; e1=0.01; c0=2.3
    resolution: Nexus file containing the resolution. This will be used to produce a elastic line.
    convolved: Nexus file containing the convolution of the simulated S(Q,E) with the resolution.
    qvalues: single-column file containing list of Q-values
    assembled: output Nexus file containing the assembled S(Q,E) of the beamline model and the simulated S(Q,E)

  Returns:
    workspace containing the assembled S(Q,E)
  """
  import numpy
  from mantid.simpleapi import (LoadNexus, ScaleX, SaveNexus)
  Q=[float(q) for q in open(qvalues,'r').read().split('\n')]
  p={}
  trace()
  for pair in open(model,'r').readline().split(';'):
    key,val=pair.split('=')
    p[key.strip()]=float(val.strip())
  wsr=LoadNexus(Filename=resolution,OutputWorkspace='resolutions')
  E=wsr.readX(0)
  wse=ScaleX(InputWorkspace=wsr, OutputWorkspace='elastics',factor=-1) # elastic line
  wsc=LoadNexus(Filename=convolved,OutputWorkspace='convolveds')
  for i in range(wsc.getNumberHistograms()):
    elastic=wse.readY(i) # elastic spectrum at a given Q
    convolved=wsc.readY(i) # convolved spectrum at a given Q
    wsc.setY(i, (p['b0']+p['b1']*E) + (p['e0']*numpy.exp(-p['e1']*Q[i])*elastic) + (p['c1']*convolved) ) # overwrite spectrum
  SaveNexus(InputWorkspace=wsc, Filename=assembled)
  return wsc

def lowTResolution(model, simulated, resolution, convolved, expdata=None,
                   costfile=None, **kwargs):
  """Convolve a simulated S(Q,E) with a resolution file

  Arguments:
    model: beamline model file (background, elastic line, convolution).
    simulated: Nexus file containing S(Q,E) from a simulation
    resolution: Nexus file containing the resolution. This will be used to produce a elastic line.
    convolved: Output Nexus file containing the convolution of the simulated S(Q,E) with the model beamline.
    expdata: Optional, experimental nexus file. If passed, output convolved will be binned as expdata.
    costfile: Optional, file to store cost. If passed, the cost of comparing convolved and expdata will be saved.
    [**kwargs]: extra options for the Mantid algorithms producing S(Q,E). For
            example:
             kwargs={'Fit':{'StartX'=-50.0, 'EndX'=50.0},
                    }

  Returns:
    Groupworkspace containing the convolved S(Q,E)
  """
  from mantid.simpleapi import (LoadNexus, ScaleX, Fit, ExtractSingleSpectrum, RenameWorkspace, AppendSpectra, SaveNexus)
  from mantidhelper.algorithm import findopts
  from mantidhelper.fitalg import parse_results
  from fitalg import parse_results
  algs_opt=locals()['kwargs']
  funcStr=open(model,'r').readline().strip() #read the model string
  wsr=LoadNexus(Filename=resolution,OutputWorkspace='resolutions')
  wse=ScaleX(InputWorkspace=wsr, OutputWorkspace='elastics',factor=-1)
  wss=LoadNexus(Filename=simulated,OutputWorkspace='simulateds')
  wsx=wss # wsx will be our reference to compare convolved in Fit algorithm
  if expdata: 
    wse=LoadNexus(Filename=expdata,OutputWorkspace='expdatas')
    wsx=wse # the reference will be the experimental data
  wsc=None # output convolved spectra
  cost=0
  for iw in range(wss.getNumberHistograms()):
    ExtractSingleSpectrum(wsr,OutputWorkspace='resolution',WorkspaceIndex=iw)
    ExtractSingleSpectrum(wse,OutputWorkspace='elastic',WorkspaceIndex=iw)
    ExtractSingleSpectrum(wss,OutputWorkspace='simulated',WorkspaceIndex=iw)
    ExtractSingleSpectrum(wsx,OutputWorkspace='reference',WorkspaceIndex=iw)
    r=Fit( funcStr, InputWorkspace='reference', CreateOutput='1', Output='fitted',
           MaxIterations=0, **findopts('Fit',algs_opt)
           )
    parsed=parse_results(r)
    cost+=parsed['Cost']
    RenameWorkspace(parsed['Calc'],OutputWorkspace='convolved')
    #ws=parse_results(r)['fitted_Workspace']
    if not wsc:
      wsc='convolveds'
      RenameWorkspace(InputWorkspace='convolved',OutputWorkspace=wsc)
    else:
      AppendSpectra(InputWorkspace1=wsc, InputWorkspace2='convolved', OutputWorkspace=wsc)
  SaveNexus(InputWorkspace=wsc, Filename=convolved)
  if costfile: open(costfile,'w').write(str(cost)+' obj-fn\n')
  return cost


if __name__ == "__main__":
  import argparse
  import sys
  from sets import Set
  from mantidhelper.algorithm import getDictFromArgparse
  p=argparse.ArgumentParser(description='Provider for services involving convolution of simulated S(Q,E) with a model beamline. Available services are: lowTresolution, modelBEC.')
  p.add_argument('service', help='name of the service to invoke')
  p.add_argument('-explain', action='store_true', help='print message explaining the arguments to pass for the particular service')
  if Set(['-h', '-help', '--help']).intersection(Set(sys.argv)): args=p.parse_args() # check if help message is requested
  if 'lowTresolution' in sys.argv:
    p.description='Convolve simulated S(Q,E) with a model beamline. Resolution must be provided via a Nexus file. Generates a Nexus file containing S(Q,E) in a Workspace2D.' # update help message
    for action in p._actions:
      if action.dest=='service': action.help='substitue "service" with "lowTresolution"' # update help message
    p.add_argument('--model',help='name of the file containing the model beamline string')
    p.add_argument('--simulated',help='name of the nexus file containing the simulated S(Q,E)')
    p.add_argument('--resolution',help='name of the nexus file containing the resolution function. This will be used to produce an elastic line.')
    p.add_argument('--convolved',help='name of the output nexus file')
    p.add_argument('--expdata',help='optional, experimental nexus file. If passed, output convolved will be binned as expdata.')
    p.add_argument('--costfile',help='optional, file to store cost. If passed, the cost of comparing convolved and expdata will be saved.')
    p.add_argument('--Fit', help='certain arguments for the Mantid Fit algorithm. Example: --Fit="StartX=-50.0,EndX=50.0"')
    if '-explain' in sys.argv:
      p.parse_args(args=('-h',))
    else:
      args=p.parse_args()
      lowTResolution(args.model, args.simulated, args.resolution, args.convolved,
                     expdata=args.expdata, costfile=args.costfile,
                     Fit=getDictFromArgparse('Fit',args)
                     )
  elif 'modelBEC' in sys.argv:
    p.description='Assemble the background, elastic line and convolution of the resolution with the simulated S(Q,E) according to model (b0+b1*E  +  e0*exp(-e1*Q^2)*Elastic(E)  +  c0*Resolution(E)xSimulated(Q,E)). Output to a Nexus file'
    for action in p._actions:
      if action.dest=='service': action.help='substitue "service" with "modelBEC"' # update help message
    p.add_argument('--model',help='name of the file containing the model beamline string')
    p.add_argument('--resolution',help='name of the nexus file containing the resolution function. This will be used to produce an elastic line.')
    p.add_argument('--convolved',help='Nexus file containing the convolution of the simulated S(Q,E) with the resolution.')
    p.add_argument('--qvalues',help='Single-column file containing list of Q-values.')
    p.add_argument('--assembled',help='output Nexus file containing the assembled S(Q,E) of the beamline model and the simulated S(Q,E)')
    if '-explain' in sys.argv:
      p.parse_args(args=('-h',))
    else:
      args=p.parse_args()
      modelBEC(args.model, args.resolution, args.convolved, args.qvalues, args.assembled)
  else:
    print 'service not found'