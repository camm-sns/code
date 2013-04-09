'''
Produce a resolution function

Create on Apr 8, 2013

@author: jmborr
'''
from pdb import set_trace as trace # uncomment only for debugging purposes

def elasticLineLowTemp(insqe, outres=None):
  '''Produces a resolution function based on the quasi-elastic signal at low temperature
  
  Argument:
    insqe: a Nexus file containing S(Q,E) at low temperature. One spectrum per Q-value.
    [outres]: output Nexus file containing Res(Q,E). Each spectrum is separately applied the Mantid::NormaliseToUnity algorithm.

  Returns:
    mantid workspace containing Res(Q,E)
  '''
  from mantid.simpleapi import (LoadNexus, ExtractSingleSpectrum, NormaliseToUnity, AppendSpectra, ScaleX, SaveNexus)
  wse=LoadNexus(Filename=insqe,OutputWorkspace='insqe')
  for iw in range(wse.getNumberHistograms()):
    iname='insqe'+str(iw)
    ExtractSingleSpectrum(wse,OutputWorkspace=iname,WorkspaceIndex=iw)
    NormaliseToUnity(InputWorkspace=iname, OutputWorkspace=iname)
    if iw:
      AppendSpectra(InputWorkspace1='insqe0', InputWorkspace2=iname, OutputWorkspace='insqe0')
  wsr=ScaleX(InputWorkspace='insqe0', OutputWorkspace='resolution',factor=-1)
  if outres:
    SaveNexus(InputWorkspace='resolution', Filename=outres)
  return wsr

if __name__ == "__main__":
  import argparse
  import sys
  from sets import Set
  p=argparse.ArgumentParser(description='Provider for services involving the production of a resolution function. Available services are: elasticLineLowTemp')
  p.add_argument('service', help='name of the service to invoke')
  p.add_argument('-explain', action='store_true', help='print message explaining the arguments to pass for the particular service')
  if Set(['-h', '-help', '--help']).intersection(Set(sys.argv)): args=p.parse_args() # check if help message is requested
  if 'elasticLineLowTemp' in sys.argv:
    p.description='Produces a resolution function based on the quasi-elastic signal at low temperature'
    for action in p._actions:
      if action.dest=='service': action.help='substitue "service" with "elasticLineLowTemp"' # update help message
    p.add_argument('--insqe',help=' Nexus file containing S(Q,E) at low temperature. One spectrum per Q-value.')
    p.add_argument('--outres',help='output Nexus file containing Res(Q,E). Each spectrum is separately applied the Mantid::NormaliseToUnity algorithm.')
    if '-explain' in sys.argv:
      p.parse_args(args=('-h',))
    else:
      args=p.parse_args()
      elasticLineLowTemp(args.insqe, outres=args.outres)
