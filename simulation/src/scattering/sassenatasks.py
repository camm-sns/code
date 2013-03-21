'''
Created on Mar 8, 2013

@author: jmborr
'''

from pdb import set_trace as trace # uncomment only for debugging purposes

def hasVersion(filename):
  """Check filename as sassena version"""
  from h5py import File
  f = File(filename,'r')
  value=False
  if 'sassena_version' in f.attrs.keys(): value=True
  f.close()
  return value

def addVersionStamp(filename,stamp):
  """ Insert stamp as version attribute in and HDF5 file. """
  from h5py import File
  f =File(filename,'r+')
  f.attrs['sassena_version']=stamp
  f.close()

def genSQE(hdfname,nxsname,wsname=None,indexes=[],**kwargs):
  """ Generate S(Q,E)

  Loads Sassena output (HDF5 file) and generates a Nexus file containing
  S(Q,E) in a Workspace2D. Options to LoadSasena and SassenaFFT algorithms
  are lumped into optional 'options' parameter

  Args:
    hdfname: path to sassena output hdf5 file
    nxsname: path to output Nexus file
    [wsname]: root name for the GroupWorkspace created when Sassena output is loaded
    [indexes]: save only spectra with indexes given by indexes list. If indexes is empty,
               all spectra are saved.
    [**kwargs]: extra options for the Mantid algorithms producing S(Q,E). For
             example:
             kwargs={'LoadSassena':{'TimeUnit':0.1,},
                     'SassenaFFT':{'Temp':290,},
                     'NormaliseToUnity:{'RangeLower'=50.0,'RangeUpper':50.0}'
                    }

  Returns:
    GroupWorkspace containing I(Q,t), S(Q,E), and Q-vectors Worskpaces, among others.
    For example:
    rooname_
            |_rootname_qvectors
            |_rootname_fqt.Re
            |_rootname_fqt.Im
            |_rootname_sqw

  Raises:
    None
  """
  from mantidhelper.algorithm import findopts
  from mantidhelper.workspace import prunespectra
  from os.path import basename,splitext
  from mantid.simpleapi import (LoadSassena, SortByQVectors, SassenaFFT, SaveNexus)
  wsname=wsname or splitext(basename(nxsname))[0]
  algs_opt=locals()['kwargs']
  ws=LoadSassena(Filename=hdfname, OutputWorkspace=wsname, **findopts('LoadSassena',algs_opt))
  SortByQVectors(ws)
  SassenaFFT(ws,**findopts('SassenaFFT',algs_opt))
  wss=wsname+'_sqw'
  if 'NormaliseToUnity' in algs_opt.keys():
    from mantid.simpleapi import (ConvertToHistogram, NormaliseToUnity)
    ConvertToHistogram(InputWorkspace=wss,OutputWorkspace=wss)
    NormaliseToUnity(InputWorkspace=wss,OutputWorkspace=wss,**findopts('NormaliseToUnity',algs_opt))
  prunespectra(InputWorkspace=wss,indexes=indexes)
  SaveNexus(InputWorkspace=wss, Filename=nxsname, **findopts('SaveNexus',algs_opt))
  return ws

# Use as a script
if __name__ == '__main__':
  import argparse
  import sys
  from mantidhelper.algorithm import getDictFromArgparse
  from sets import Set
  #trace()
  p=argparse.ArgumentParser(description='Provider for services involving Sassena IO. Available services are: genSQE, SassenaVersion ')
  p.add_argument('service', help='name of the function in this module to call')
  p.add_argument('-explain', action='store_true', help='print message explaining the arguments to pass for the particular service')
  if Set(['-h', '-help', '--help']).intersection(Set(sys.argv)): args=p.parse_args() # check if help message is requested
  if 'SassenaVersion' in sys.argv:
    p.description='Loads Sassena output (HDF5 file) and adds Sassena Version number.' # update help message
    for action in p._actions:
      if action.dest=='service': action.help='substitue SERVICE by SassenaVersion' # update help message
    p.add_argument('hdfname', help='path to sassena output hdf5 file')
    # Check if help message is requested
    if '-explain' in sys.argv:
      p.parse_args(args=('-h',))
    else:
      args=p.parse_args()
      if not hasVersion(args.hdfname): addVersionStamp(args.hdfname,'1.4.1')
  elif 'genSQE' in sys.argv:
    p.description='Loads Sassena output (HDF5 file) and generates a Nexus file containing S(Q,E) in a Workspace2D.' # update help message
    for action in p._actions:
      if action.dest=='service': action.help='substitue SERVICE by genSQE' # update help message
    p.add_argument('hdfname', help='path to sassena output hdf5 file')
    p.add_argument('nxsname', help='path to output Nexus file')
    p.add_argument('--wsname', help='root name for the GroupWorkspace created when Sassena output is loaded')
    p.add_argument('--indexes', help='space separated list of workspace indexes to keep. Example: --indexes "2 4 6 8". If not declared, all indexes are kept')
    p.add_argument('--LoadSassena', help='certain arguments for the algorithm. Example --LoadSassena="TimeUnit:0.1"')
    p.add_argument('--SassenaFFT', help='certain arguments for the algorithm. Example: --SassenaFFT="FTTonlyRealPart:True,DetailedBalance:True,Temp:290"')
    p.add_argument('--NormaliseToUnity', help='certain arguments for the algorithm. Example: --NormaliseToUnity="RangeLower:-50.0,RangeUpper:50.0"')
    p.add_argument('--SaveNexus', help='certain arguments for the algorithm. Example: --SaveNexus="Title:some title here"')
    # Check if help message is requested
    if '-explain' in sys.argv:
      p.parse_args(args=('-h',))
    else:
      args=p.parse_args()
      indexes=[]
      if args.indexes: indexes=[int(i) for i in args.indexes.split()]
      genSQE(args.hdfname, args.nxsname, wsname=args.wsname, indexes=indexes,
             LoadSassena=getDictFromArgparse('LoadSassena',args),
             SassenaFFT=getDictFromArgparse('SassenaFFT',args),
             SaveNexus=getDictFromArgparse('SaveNexus',args),
             NormaliseToUnity=getDictFromArgparse('NormaliseToUnity',args)
             )
