'''
Created on Mar 8, 2013

@author: jmborr
'''
import h5py 

#from pdb import set_trace as trace # uncomment only for debugging purposes

def hasVersion(filename):                                                                                                       
  """Check filename as sassena version"""                                                                                       
  f = h5py.File(filename,'r')                                                                                                   
  value=False                                                                                                                   
  if 'sassena_version' in f.attrs.keys(): value=True                                                                            
  f.close()                                                                                                                     
  return value                                                                                                                  

def addVersionStamp(filename,stamp):                                                                                            
  """ Insert stamp as version attribute in and HDF5 file. """                                                                   
  f = h5py.File(filename,'r+')                                                                                                  
  f.attrs['sassena_version']=stamp                                                                                              
  f.close()                                                                                                                     

def genSQE(hdfname,nxsname,wsname=None,**kwargs):
  """ Generate S(Q,E)

  Loads Sassena output (HDF5 file) and generates a Nexus file containing
  S(Q,E) in a Workspace2D. Options to LoadSasena and SassenaFFT algorithms
  are lumped into optional 'options' parameter

  Args:
    hdfname: path to sassena output hdf5 file
    nxsname: path to output Nexus file
    [wsname]: root name for the GroupWorkspace created when Sassena output is loaded
    [**kwargs]: extra options for the Mantid algorithms producing S(Q,E). For
             example:
             kwargs={'LoadSassena':{'TimeUnit':0.1,},
                     'SassenaFFT':{'Temp':290,}
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
  def findopts(algname,options):
    """ Find if options were passed for the algorithm algname. """
    if algname in options.keys():
      return algs_opt[algname]
    return {}

  from os.path import basename,splitext
  from mantid.simpleapi import (LoadSassena, SortByQVectors, SassenaFFT, SaveNexus)
  if not hasVersion(hdfname): addVersionStamp(hdfname,'1.4.1')
  wsname=wsname or splitext(basename(nxsname))[0]
  algs_opt=locals()['kwargs']
  ws=LoadSassena(Filename=hdfname, OutputWorkspace=wsname, **findopts('LoadSassena',algs_opt))
  SortByQVectors(ws)
  SassenaFFT(ws,**findopts('SassenaFFT',algs_opt))
  SaveNexus(InputWorkspace=wsname+'_sqw', Filename=nxsname, **findopts('SaveNexus',algs_opt))
  return ws

# Use as a script
if __name__ == '__main__':
  import argparse
  import sys
  from mantidhelper.algorithm import getDictFromArgparse
  from sets import Set
  p=argparse.ArgumentParser(description='Provider for services involving Sassena IO. Available services are: genSQE, ')
  p.add_argument('service', help='name of the function in this module to call')
  p.add_argument('-explain', action='store_true', help='print message explaining the arguments to pass for the particular service')
  if Set(['-h', '-help', '--help']).intersection(Set(sys.argv)): args=p.parse_args() # check if help message is requested
  if 'genSQE' in sys.argv:
    p.description='Loads Sassena output (HDF5 file) and generates a Nexus file containing S(Q,E) in a Workspace2D.' # update help message
    for action in p._actions:
      if action.dest=='service': action.help='substitue SERVICE by genSQE' # update help message
    p.add_argument('hdfname', help='path to sassena output hdf5 file')
    p.add_argument('nxsname', help='path to output Nexus file')
    p.add_argument('--wsname', help='root name for the GroupWorkspace created when Sassena output is loaded')
    p.add_argument('--LoadSassena', help='certain arguments for the algorithm. Example --LoadSassena="TimeUnit:0.1"')
    p.add_argument('--SassenaFFT', help='certain arguments for the algorithm. Example: --SassenaFFT="FTTonlyRealPart:True,DetailedBalance:True,Temp:290"')
    p.add_argument('--SaveNexus', help='certain arguments for the algorithm. Example: --SaveNexus="Title:some title here"')
    # Check if help message is requested
    if '-explain' in sys.argv:
      p.parse_args(args=('-h',))
    else:
      args=p.parse_args()
      genSQE(args.hdfname, args.nxsname, wsname=args.wsname,
             LoadSassena=getDictFromArgparse('LoadSassena',args),
             SassenaFFT=getDictFromArgparse('SassenaFFT',args),
             SaveNexus=getDictFromArgparse('SaveNexus',args)
             )