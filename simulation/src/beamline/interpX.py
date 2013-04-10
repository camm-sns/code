'''Interpolate a workspace along certain axis

Created on Apr 9, 2013

@author: jmborr
'''
from pdb import set_trace as trace # uncomment only for debugging purposes

def itp_simple(workspace,shift):
  '''For all spectra of a mantid workspace, shift a small amount and interpolate through Mantid::Rebin

  This function is appropriate for shifts of the order of the bin size. The workspace is
  (1) shifted and (2) rebinned to recover the previous bin partition of the X-axis.
  It is assumed a constant bin size for the X-axis.

  Arguments:
    workspace: Mantid workspace
    shift: real quantity to shift along the X-axis

  Returns:
    workspace object shifted and interpolated
  '''
  wname=workspace.getName()
  width=workspace.readX(0)[1]-workspace.readX(0)[0] # assume constant bin size
  start=workspace.readX(0)[0]
  end=workspace.readX(0)[-1]
  from mantid.simpleapi import (ScaleX, Rebin)
  ScaleX(InputWorkspace=wname,OutputWorkspace=wname,factor=shift,Operation='Add')
  return Rebin(InputWorkspace=wname,OutputWorkspace=wname,Params=[start,width,end])


if __name__ == "__main__":
  import argparse
  import sys
  import re
  from sets import Set
  p=argparse.ArgumentParser(description='Provider for services involving shift of calculated S(Q,E) model Available services are: itp_simple')
  p.add_argument('service', help='name of the service to invoke')
  p.add_argument('-explain', action='store_true', help='print message explaining the arguments to pass for the particular service')
  if Set(['-h', '-help', '--help']).intersection(Set(sys.argv)): args=p.parse_args() # check if help message is requested

  if 'itp_simple' in sys.argv:
    p.description='For all spectra of a mantid workspace, shift a small amount and interpolate through Mantid::Rebin' # update help message
    for action in p._actions:
      if action.dest=='service': action.help='substitue "service" with "itp_simple"' # update help message
    p.add_argument('--assembled',help='name of the Nexus file containing assembled S(Q,E) model')
    p.add_argument('--model', help='file name for the model beamline string. Should contain "eshift=X", with X being the current value of the shift')
    p.add_argument('--interpolated',help='name of the Nexus file to output the interpolated S(Q,E) model')
    p.add_argument('--expdata',help='optional, experimental nexus file. If passed, output convolved will be binned as expdata.')
    p.add_argument('--costfile',help='optional, file to store cost. If passed, the cost of comparing convolved and expdata will be saved.')
    if '-explain' in sys.argv:
      p.parse_args(args=('-h',))
    else:
      args=p.parse_args()
      from mantid.simpleapi import (LoadNexus, SaveNexus, DakotaChiSquared)
      #trace()
      eshift=float(re.search('eshift\s*=\s*(-*\d+\.*\d+[e|E]*-*\d*)', open(args.model,'r').read()).groups()[0])
      print eshift
      ws=LoadNexus(Filename=args.assembled)
      ws=itp_simple(ws, eshift)
      SaveNexus(InputWorkspace=ws.getName(),Filename=args.interpolated)
      if args.expdata and args.costfile:
        DakotaChiSquared(DataFile=args.expdata,CalculatedFile=args.interpolated,OutputFile=args.costfile)

