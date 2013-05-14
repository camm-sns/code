'''
Estimate initial parameters for a model beamline

Created on May 13, 2013

@author: jmborr
'''

from pdb import set_trace as trace # uncomment only for debugging purposes

def modelB_freeE_C(modeltpl, resolution, pdb, qlist, expdata, initparfile=None):
  """Estimate initial beamline parameters for the modelB_freeE_C
  This is a hard-coded model consisting of a linear background, and elastic line, and a convolution:
    b0+b1*E  +  +e0(Q)*Elastic(E)  +  c0*Resolution(E)xSimulated(Q,E)
    We load Resolution(E)xSimulated(Q,E) as Convolved(Q,E)
    e0(Q) are a set of fitting parameters, one for each Q
  Initial values are estimated as follows:
  b0:0.0
  b1:0.0
  Integration of the model with no background along the Energy axes results in:
    e0*Int_{elastic} + c0*Int_{resolution}*I(Q,t=0) ~ Int_{expdata},
    with I(Q,t) the simulated intermediate resolution function
  For the lowest Q, we assume contributions fromt the elastic line and simuation are equal. Thus:
    c0*Int_{resolution}*I(Q,t=0) ~ 1/2*Int_{expdata} ---> provides estimation for c0
    e0(Qmin) ~ 1/2*Int_{expdata} ---> provides estimation for e0
  For the remaining Q, we use the previous formula substituting the c0 found above
  eshift:0.0
  
  Arguments:
    model: beamline template model file (xml format)
    resolution: Nexus file containing the model resolution
    pdb: PDB file containing conformation of the system
    qlist: list of Q-values
    expdata: Nexus file containing the experimental data
    [initparfile]: Output the initial parameters as a string in file with name initparfile

  Returns:
    initparms: string with initial values for the parameters
  """
  from simulation.src.scattering.sassenatasks import calculateIQ
  from simulation.src.molmec.ffupdate.ff_update import loadFFtpl,updateTemplate
  from mantid.simpleapi import LoadNexus,Integration,Plus

  wsr=LoadNexus(Filename=resolution,OutputWorkspace='resolution')
  wsri=Integration(wsr,OutputWorkspace='resolution_integrated')
  wse=LoadNexus(Filename=expdata,OutputWorkspace='experiment')
  wsei=Integration(wse,OutputWorkspace='experiment_integrated')
  incws,cohws=calculateIQ(qlist, pdb) # calculate I(Q) for the PDB structure

  parl,template=loadFFtpl(modeltpl)
  pard={}
  for par in parl: pard[par._name]=par
  nhist=wsri.getNumberHistograms()
  pard['b0'].setValue(1e-10) # needs to be positive
  pard['b1'].setValue(0.)
  trace()
  pard['c0'].setValue(0.5*wsei.readY(0)[0]/(wssi.readY(0)[0]*wsri.readY(0)[0]))
  pard['e0.0'].setValue(0.5*wsei.readY(0)[0]/wsri.readY(0)[0])
  for ihist in range(1,nhist ):
    pard['e0.'+str(ihist)].setValue(wsei.readY(ihist)[0]/wsri.readY(0)[0] - pard['c0']._value*wssi.readY(0)[0])
  pard['eshift'].setValue(0.)
  template=updateTemplate(template,parl)

  if initparfile: open(initparfile,'w').write(template)
  return template


if __name__ == "__main__":

  import argparse
  import sys
  from sets import Set

  p=argparse.ArgumentParser(description='Provider for services involving initialization of model beamline parameters. Available models are: modelB_freeE_C')
  p.add_argument('service', help='name of the service to invoke')
  p.add_argument('-explain', action='store_true', help='print message explaining the arguments to pass for the particular service')
  if Set(['-h', '-help', '--help']).intersection(Set(sys.argv)): args=p.parse_args() # check if help message is requested

  if 'modelB_freeE_C' in sys.argv:
    p.description='''Estimate initial beamline parameters for the modelB_freeE_C.
  This is a hard-coded model consisting of a linear background, an elastic line, and a convolution:
    b0+b1*E  +  +e0(Q)*Elastic(E)  +  c0*Resolution(E)xSimulated(Q,E).
    We load Resolution(E)xSimulated(Q,E) as Convolved(Q,E).
    e0(Q) are a set of fitting parameters, one for each Q.
  Initial values are estimated as follows:
  b0:0.0,
  b1:0.0.
  Integration of the model with no background along the Energy axes results in:
    e0*Int_{elastic} + c0*Int_{resolution}*I(Q,t=0) ~ Int_{expdata},
    with I(Q,t) the simulated intermediate resolution function.
  For the lowest Q, we assume contributions fromt the elastic line and simuation are equal. Thus:
    c0*Int_{resolution}*I(Q,t=0) ~ 1/2*Int_{expdata} ---> provides estimation for c0,
    e0(Qmin) ~ 1/2*Int_{expdata} ---> provides estimation for e0.
  For the remaining Q, we use the previous formula substituting the c0 found above.
  eshift:0.0'''
    for action in p._actions:
      if action.dest=='service': action.help='substitue "service" with "modelB_freeE_C"' # update help message
    p.add_argument('--model',       help='beamline template model file (xml format)')
    p.add_argument('--resolution',  help='name of the nexus file containing the resolution function')
    p.add_argument('--qlist',       help='list of Q-values, space separated and withing quotes')
    p.add_argument('--pdb',         help='file in Proteind Database (PDB) ASCII format containing conformation of the system')
    p.add_argument('--expdata',     help='experimental nexus file')
    p.add_argument('--initparfile', help='Filename where to output the estimated initial parameters as a string')
    if '-explain' in sys.argv:
      p.parse_args(args=('-h',))
    else:
      args=p.parse_args()
      qlist=[float(x) for x in args.qlist.split()]
      modelB_freeE_C(args.model, args.resolution, args.pdb, qlist, args.expdata, initparfile=args.initparfile)

  else:
    print 'service not found'

























