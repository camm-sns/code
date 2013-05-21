'''
Estimate initial parameters for a model beamline

Created on May 13, 2013

@author: jmborr
'''

from pdb import set_trace as trace # uncomment only for debugging purposes

from kernel.logger import SimpleLogger
g_log=SimpleLogger('initparams')

def modelB_freeE_C(modeltpl, elastic, convolved, expdata, initparfile=None):
  """Estimate initial beamline parameters for the modelB_freeE_C
  This is a hard-coded model consisting of a linear background, and elastic line, and a convolution:
    b0+b1*E  +  +e0(Q)*Elastic(E)  +  c0*Resolution(E)xSimulated(Q,E)
    We load Resolution(E)xSimulated(Q,E) as Convolved(Q,E)
    e0(Q) are a set of fitting parameters, one for each Q
  Initial values are estimated as follows:
  b0:0.0
  b1:0.0
  Evaluation of the model at E=0:
    e0*elastic(Q,0) + c0*convolved(Q,0) ~ experiment(Q,0) {Eq.1},
    with 'convolved' the convolution of the experimental resolution and the Fourier transform
    of the simulated intermediate structure factor
  For the lowest Q, we assume contributions fromt the elastic line and simuation are equal. Thus:
    c0*convolved(Qmin,0) ~ 1/2*experiment(Qmin,0) ---> provides estimation for c0
    e0(Qmin)*elastic(Qmin,0) ~ 1/2*experiment(Qmin,0) ---> provides estimation for e0
  For the remaining Q, we use {Eq.1} substituting the c0 found above.
  Finally, eshift:0.0
  
  Arguments:
    model: beamline template model file (xml format)
    elastic: Nexus file containing the elastic line
    convolved: Nexus file containing convolution of the resolution and simulated structure factor
    expdata: Nexus file containing the experimental data
    [initparfile]: Output the initial parameters as a string in file with name initparfile

  Returns:
    initparms: string with initial values for the parameters
  """
  from simulation.src.molmec.ffupdate.ff_update import loadFFtpl,updateTemplate
  from mantid.simpleapi import LoadNexus

  wse=LoadNexus(Filename=elastic,OutputWorkspace='elastic')
  wsc=LoadNexus(Filename=convolved,OutputWorkspace='convolved')
  wsx=LoadNexus(Filename=expdata,OutputWorkspace='experiment')

  parl,template=loadFFtpl(modeltpl)
  pard={}
  for par in parl: pard[par._name]=par

  nhist=wsx.getNumberHistograms()
  le=len(wsx.readX(0))
  for ws in wse,wsc:
    if ws.getNumberHistograms()!=nhist or len(ws.readX(0))!=le:
      error_message='%s %d histograms of length %d do not conform to those of experiment'%(ws.getName(),ws.getNumberHistograms(),len(ws.readX(0)))
      ws.getName()+' histograms do not conform to those of experiment'
      g_log.error(error_message)
      raise StandardError(error_message)

  pard['b0'].setValue(1e-10) # needs to be positive
  pard['b1'].setValue(0.)
  ezero=le/2 # assume E=0 in the middle of the histogram span
  pard['c0'].setValue(0.5*wsx.readY(0)[ezero]/wsc.readY(0)[ezero])
  pard['e0.0'].setValue(0.5*wsx.readY(0)[ezero]/wse.readY(0)[ezero])
  trace()
  for ihist in range(1,nhist):
    pard['e0.'+str(ihist)].setValue((wsx.readY(ihist)[ezero] - pard['c0']._value*wsc.readY(ihist)[ezero]) / wse.readY(ihist)[ezero])
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
    p.description='''Estimate initial beamline parameters for the modelB_freeE_C
  This is a hard-coded model consisting of a linear background, and elastic line, and a convolution:
    b0+b1*E  +  +e0(Q)*Elastic(E)  +  c0*Resolution(E)xSimulated(Q,E)
    We load Resolution(E)xSimulated(Q,E) as Convolved(Q,E)
    e0(Q) are a set of fitting parameters, one for each Q
  Initial values are estimated as follows:
  b0:0.0
  b1:0.0
  Evaluation of the model at E=0:
    e0*elastic(Q,0) + c0*convolved(Q,0) ~ experiment(Q,0) {Eq.1},
    with 'convolved' the convolution of the experimental resolution and the Fourier transform
    of the simulated intermediate structure factor
  For the lowest Q, we assume contributions fromt the elastic line and simuation are equal. Thus:
    c0*convolved(Qmin,0) ~ 1/2*experiment(Qmin,0) ---> provides estimation for c0
    e0(Qmin)*elastic(Qmin,0) ~ 1/2*experiment(Qmin,0) ---> provides estimation for e0
  For the remaining Q, we use {Eq.1} substituting the c0 found above.
  Finally, eshift:0.0'''
    for action in p._actions:
      if action.dest=='service': action.help='substitue "service" with "modelB_freeE_C"' # update help message
    p.add_argument('--model',       help='beamline template model file (xml format)')
    p.add_argument('--elastic',     help='Nexus file containing the elastic line')
    p.add_argument('--convolved',   help='Nexus file containing convolution of the resolution and simulated structure factor')
    p.add_argument('--expdata',     help='experimental nexus file')
    p.add_argument('--initparfile', help='Filename where to output the estimated initial parameters as a string')
    if '-explain' in sys.argv:
      p.parse_args(args=('-h',))
    else:
      args=p.parse_args()
      modelB_freeE_C(args.model, args.elastic, args.convolved, args.expdata, initparfile=args.initparfile)

  else:
    print 'service not found'

























