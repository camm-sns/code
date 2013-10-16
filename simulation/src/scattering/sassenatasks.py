'''
Created on Mar 8, 2013

@author: jmborr
'''

from pdb import set_trace as trace # uncomment only for debugging purposes
import os

sassexec=None
sassdb=None
catdcd=None

def tempfile():
  try:
    from tempdir import mkstemp
    handle,outfile=mkstemp(dir='/tmp') # temporaty output file
  except:
    import datetime, calendar
    timestamp=calendar.timegm( datetime.datetime.now().utctimetuple())
    outfile='/tmp/tmp.'+str(timestamp)
  return outfile

def setDataBasePath(sassena_libray):
  """ Set the directory where the Sassena database is located """
  sassdb=sassena_library

def setSassExec(filepath=None):
  """Set global variable sassexec by providing the path or finding it under PATH environment variable"""
  if filepath:
    if os.path.exists(filepath) and os.access(filepath, os.X_OK):
      globals()['sassexec']=filepath
      return filepath
  if globals()['sassexec']: return None # no need to set in initialized
  for path in os.environ["PATH"].split(os.pathsep):
    path=path.strip('"')
    fpath=os.path.join(path, 'sassena')
    if os.path.exists(fpath) and os.access(fpath, os.X_OK):
      globals()['sassexec']=fpath
      break
  return globals()['sassexec']

def setSassDB(filepath=None):
  if filepath:
    if os.path.exists(filepath) and os.access(filepath, os.R_OK):
      globals()['sassdb']=filepath
  if "SASSENA_DB_DIR" in os.environ.keys(): globals()['sassdb']=os.environ["SASSENA_DB_DIR"]
  return globals()['sassdb']

def setCatDCD(filepath=None):
  """Set global variable catdcd by providing the path or finding it under PATH environment variable"""
  if filepath:
    if os.path.exists(filepath) and os.access(fpath, os.X_OK):
      globals()['catdcd']=filepath
      return filepath
  if globals()['catdcd']: return None # no need to set in initialized
  for path in os.environ["PATH"].split(os.pathsep):
    path=path.strip('"')
    fpath=os.path.join(path, 'catdcd')
    if os.path.exists(fpath) and os.access(fpath, os.X_OK):
      globals()['catdcd']=fpath
      break
  return globals()['catdcd']

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

def isOrderedByQmodulus(filename):
  """ Check list of structure factors is ordered by increasing modulus of momentum transfer

  Arguments:
    filename: a Sassena output file

  Returns:
   True if qvectors dataset is ordered by increasing modulus of
        momentum transfer. Otherwise returns False
  """
  from h5py import File
  import numpy
  f=File(filename,'r')
  ds_q = numpy.array(f["qvectors"]) # shape==(nvectors,3)
  f.close()
  moduli=numpy.square(ds_q).sum(axis=1) # moduli-squared of the Q-vectors
  return all(x<=y for x, y in zip(moduli, moduli[1:]))

def orderByQmodulus(filename,outfile=None):
  """ Sassena does not enforce any ordering of the structure factors.
  Here we order by increasing value of modulus of Q-vectors. """
  from h5py import File
  import numpy
  f=File(filename,'r')
  overwrite=False
  if not outfile:
    outfile=tempfile() # temporaty output file
    overwrite=True
  g=File(outfile,'w')
  ds_q = numpy.array(f["qvectors"]) # shape==(nvectors,3)
  moduli=numpy.square(ds_q).sum(axis=1) # moduli-squared of the Q-vectors
  rank=numpy.argsort(moduli) # rank from smallest to greatest
  for dset in ('qvectors', 'fqt', 'fq', 'fq0', 'fq2'):
    if dset in f.keys(): 
      x=numpy.array(f[dset])
      if not outfile:
        del f[dset]
        f[dset]=x[rank]
      else:
        g[dset]=x[rank]
  for key,val in f.attrs.items(): g.attrs[key]=val
  g.close()
  f.close()
  if overwrite:
    os.system('/bin/mv %s %s'%(outfile,filename))
  return None

def calculateIQ(qlist, pdbfile):
  """Calculate both the static coherent and static incoherent intermediate structure factors
  Arguments:
    qslit: list of Q=values
    pdbfile: conformation for which to calculate I(Q)

  Returns:
    incoherent and coherent Mantid WorkspaceGroups, in this order
  """
  import sys
  from tempfile import mkdtemp
  from os.path import exists
  from mantid.simpleapi import LoadSassena,SortByQVectors,mtd

  inc_template='''<root>
<sample>
  <structure>
    <file>_PDB_</file>
    <format>pdb</format>
  </structure>
  <framesets>
    <frameset>
    <file>_DCD_</file>
    <format>dcd</format>
    </frameset>
  </framesets>
</sample>
<stager>
  <target>system</target>
</stager>
<scattering>
  <type>self</type>
  <dsp>
    <type>autocorrelate</type>
    <method>fftw</method>
  </dsp>
  <vectors>
    <type>file</type>
    <file>_QLIST_</file>
  </vectors>
  <average>
    <orientation>
    <type>vectors</type>
    <vectors>
    <type>sphere</type>
    <algorithm>boost_uniform_on_sphere</algorithm>
    <resolution>500</resolution>
    <seed>5</seed>
    </vectors>
    </orientation>
  </average>
  <signal>
    <file>_FQINC_</file>
    <fqt>false</fqt>
    <fq0>true</fq0>
    <fq>false</fq>
    <fq2>false</fq2>
  </signal>
</scattering>
<database>
  <type>file</type>
  <file>_DATABASEDIR_/db-neutron-incoherent.xml</file>
</database>
</root>'''

  coh_template='''<root>
<sample>
  <structure>
    <file>_PDB_</file>
    <format>pdb</format>
  </structure>
  <framesets>
    <frameset>
    <file>_DCD_</file> 
    <format>dcd</format>
    </frameset>
  </framesets>
</sample>
<stager>
  <target>system</target>
</stager>
<scattering>
  <type>all</type>
  <dsp>
    <type>autocorrelate</type>
    <method>fftw</method>
  </dsp>
  <vectors>
    <type>file</type>
    <file>_QLIST_</file>
  </vectors>
  <average>
    <orientation>
    <type>vectors</type>
    <vectors>
    <type>sphere</type>
    <algorithm>boost_uniform_on_sphere</algorithm>
    <resolution>500</resolution>
    <seed>5</seed>
    </vectors>
    </orientation>
  </average>
  <signal>
    <file>_FQCOH_</file>
    <fqt>false</fqt>
    <fq0>true</fq0>
    <fq>false</fq>
    <fq2>false</fq2>
  </signal>
</scattering>
<database>
  <type>file</type>
  <file>_DATABASEDIR_/db-neutron-coherent.xml</file>
</database>
</root>'''

  catdcd=setCatDCD() # set variable catdcd with the path to executable catdcd
  if not catdcd:
    sys.stderr.write('executable "catdcd" not found')
    return None

  sassexec=setSassExec() # set variable sassexec with the path to executable sassena
  if not sassexec: 
    sys.stderr.write('executable "sassena" not found')
    return None

  sassdb=setSassDB() # set variable sassdb with the path to the sassena database
  if not sassdb: 
    sys.stderr.write('directory containing the sassena database not found. Set SASSENA_DB_DIR environment variable first')
    return None

  workdir=mkdtemp(prefix='calculateIQ', dir='/tmp') # temporary workding directory
  os.system('%s -o %s/dcd -pdb %s'%(globals()['catdcd'],workdir,pdbfile)) # create dcd one-frame trajectory
  open(workdir+'/qlist.dat','w').write('\n'.join([ str(q)+' 0. 0.' for q in qlist])) # save list of Q to file
  os.system('/bin/cp %s %s/pdb'%(pdbfile,workdir))
  pairs={'_PDB_':os.path.join(workdir,'pdb'),
         '_DCD_':os.path.join(workdir,'dcd'),
         '_QLIST_':os.path.join(workdir,'qlist.dat'),
         '_FQINC_':os.path.join(workdir,'fq_inc.h5'),
         '_FQCOH_':os.path.join(workdir,'fq_coh.h5'),
         '_DATABASEDIR_':sassdb,
         }

  options=inc_template
  for (key,val) in pairs.items(): options=options.replace(key,val)
  open(workdir+'/sassena_inc.xml','w').write(options)
  os.system('%s --config=%s/sassena_inc.xml'%(sassexec,workdir)) # run sassena
  addVersionStamp(os.path.join(workdir,'fq_inc.h5'),'1.4.1')
  
  options=coh_template
  for (key,val) in pairs.items(): options=options.replace(key,val)
  open(workdir+'/sassena_coh.xml','w').write(options)
  os.system('%s --config=%s/sassena_coh.xml'%(sassexec,workdir))
  addVersionStamp(os.path.join(workdir,'fq_coh.h5'),'1.4.1')

  LoadSassena(Filename=os.path.join(workdir,'fq_inc.h5'),OutputWorkspace='inc')
  SortByQVectors(InputWorkspace='inc')
  LoadSassena(Filename=os.path.join(workdir,'fq_coh.h5'),OutputWorkspace='coh')
  SortByQVectors(InputWorkspace='coh')

  os.system('/bin/rm -rf '+workdir)
  return mtd['inc'],mtd['coh']

def genSQE(hdfname,nxsname,wsname=None,indexes=[],rebinQ=None,scale=1.0, **kwargs):
  """ Generate S(Q,E)

  Loads Sassena output (HDF5 files) and generates a Nexus file containing
  S(Q,E) in a Workspace2D. Options to LoadSasena and SassenaFFT algorithms
  are lumped into optional 'options' parameter

  Args:
    hsdfname:   path to sassena output hdf5 files for the incoherent factors. If more than one,
                 enclosed then in quotes and separate with space(s). The output S(Q,E) will be
                 the Fourier transform of the summ of the incoherent factors.
    nxsname:    path to output Nexus file
    [wsname]:   root name for the GroupWorkspace created when Sassena output is loaded
    [rebinQ]:   rebin in Q. Useful when reported experimental S(Q,E) was obtained integrating
                 over different [Q-dQ,Q+dQ] ranges. Format is "Qmin Qwidth Qmax".
    [indexes]:  save only spectra with indexes given by indexes list. If indexes is empty,
                 all spectra are saved.
    [scale]:    multipy the generated S(Q,E) by this scaling factor
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
  from mantid.simpleapi import LoadSassena,SortByQVectors,CheckWorkspacesMatch,Plus,SassenaFFT,SaveNexus,Scale
  wsname=wsname or splitext(basename(nxsname))[0]
  algs_opt=locals()['kwargs']
  hdfs=hdfname.split() # list of sassena output files serving as input
  if not isOrderedByQmodulus(hdfs[0]):
    orderByQmodulus(hdfs[0])
  ws=LoadSassena(Filename=hdfs[0], OutputWorkspace=wsname, **findopts('LoadSassena',algs_opt)) # initialize the first
  #SortByQVectors(ws)

  if len(hdfs)>1: # add remaining sassena output files
    for hdf in hdfs[1:]:
      if not isOrderedByQmodulus(hdf):
        orderByQmodulus(hdf)
      ws1=LoadSassena(Filename=hdf, **findopts('LoadSassena',algs_opt))
      #SortByQVectors(ws1)
      if CheckWorkspacesMatch(Workspace1=wsname+'_qvectors',Workspace2=ws1.getName()+'_qvectors'):
        for wstype in ('_fq0','_fqt.Re','_fqt.Im'):
          Plus(LHSWorkspace=wsname+wstype,RHSWorkspace=ws1.getName()+wstype,OutputWorkspace=wsname+wstype)
      else:
        print 'Workspaces do not match'

  if rebinQ: # rebin in Q space
    rebinQ=','.join(rebinQ.split()) #substitute separators, from space to comma
    from mantid.simpleapi import (Transpose, Rebin)
    Rebin(InputWorkspace=wsname+'_fq0',Params=rebinQ,OutputWorkspace=wsname+'_fq0')
    for wstype in ('_fqt.Re','_fqt.Im'):
      Transpose(InputWorkspace=wsname+wstype,OutputWorkspace=wsname+wstype)
      Rebin(InputWorkspace=wsname+wstype,Params=rebinQ,OutputWorkspace=wsname+wstype)
      Transpose(InputWorkspace=wsname+wstype,OutputWorkspace=wsname+wstype)
  SassenaFFT(ws,**findopts('SassenaFFT',algs_opt))
  wss=wsname+'_sqw'

  if 'NormaliseToUnity' in algs_opt.keys():
    from mantid.simpleapi import (ConvertToHistogram, NormaliseToUnity)
    ConvertToHistogram(InputWorkspace=wss,OutputWorkspace=wss)
    NormaliseToUnity(InputWorkspace=wss,OutputWorkspace=wss,**findopts('NormaliseToUnity',algs_opt))

  prunespectra(InputWorkspace=wss,indexes=indexes) # does nothing in indexes is empty
  if scale!=1.0: wss=Scale(wss,Factor=scale,Operation='Multiply')

  SaveNexus(InputWorkspace=wss, Filename=nxsname, **findopts('SaveNexus',algs_opt))
  return ws

# Use as a script
if __name__ == '__main__':
  import argparse
  import sys
  from mantidhelper.algorithm import getDictFromArgparse
  from sets import Set
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
    p.add_argument('hdfname',            help='path to sassena output hdf5 files for the incoherent factors. If more than one file is passed, enclosed then in quotes and separate them with space(s). The output S(Q,E) will be the Fourier transform of the summ of the incoherent factors.')
    p.add_argument('nxsname',            help='path to output Nexus file')
    p.add_argument('--wsname',           help='root name for the GroupWorkspace created when Sassena output is loaded')
    p.add_argument('--indexes',          help='space separated list of workspace indexes to keep. Example: --indexes "2 4 6 8". If not declared, all indexes are kept')
    p.add_argument('--rebinQ',           help='useful when reported experimental S(Q,E) was obtained integrating over different [Q-dQ,Q+dQ] ranges. Format is "Qmin Qwidth Qmax".')
    p.add_argument('--scale',            help='scale S(Q,E) by this factor. Default=1.0',default=1.0,type=float)
    p.add_argument('--LoadSassena',      help='certain arguments for the algorithm. Example --LoadSassena="TimeUnit:0.1"')
    p.add_argument('--SassenaFFT',       help='certain arguments for the algorithm. Example: --SassenaFFT="FTTonlyRealPart:True,DetailedBalance:True,Temp:290"')
    p.add_argument('--NormaliseToUnity', help='certain arguments for the algorithm. Example: --NormaliseToUnity="RangeLower:-50.0,RangeUpper:50.0"')
    p.add_argument('--SaveNexus',        help='certain arguments for the algorithm. Example: --SaveNexus="Title:some title here"')
    # Check if help message is requested
    if '-explain' in sys.argv:
      p.parse_args(args=('-h',))
    else:
      args=p.parse_args()
      indexes=[]
      if args.indexes: indexes=[int(i) for i in args.indexes.split()]
      genSQE(args.hdfname, args.nxsname, wsname=args.wsname, indexes=indexes, rebinQ=args.rebinQ, scale=args.scale,
             LoadSassena=getDictFromArgparse('LoadSassena',args),
             SassenaFFT=getDictFromArgparse('SassenaFFT',args),
             SaveNexus=getDictFromArgparse('SaveNexus',args),
             NormaliseToUnity=getDictFromArgparse('NormaliseToUnity',args)
             )
