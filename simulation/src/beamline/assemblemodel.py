'''
Convolve the simulated S(Q,E) with a model beamline

Created on Mar 19, 2013

@author: jmborr
'''
from pdb import set_trace as trace # uncomment only for debugging purposes

def writeworkspace_singlecolumn(workspace):
  buf=''
  for i in range(workspace.getNumberHistograms()):
    buf += '\n'.join([str(x) for x in workspace.readY(i)]) + '\n'
  return buf

def modelB_freeE_C(model, resolution, convolved, convolved2, assembled, expdata=None, costfile=None, derivdata=None, derivexclude=[], doshift=None):
  """Assemble the Background, Elastic line and Convolution of the resolution with the simulated S(Q,E)
  This is a hard-coded model consisting of a linear background, and elastic line, and a convolution:
    b0+b1*E  +  +e0(Q)*Elastic(E)  +  c0*Resolution(E)xSimulated(Q,E)
    We load Resolution(E)xSimulated(Q,E) as Convolved(Q,E)
    e0(Q) are a set of fitting parameters, one for each Q
    
  Arguments:
    model: beamline model file is a single line, e.g,
           b0=1.3211; b1=0.00; e0.0=0.99; e0.1=0.99; e0.2=0.99;...e0.N=0.99; e1=1.9; c0=2.3
    resolution: Nexus file containing the resolution. This will be used to produce a elastic line.
    convolved: Nexus file containing the convolution of the simulated S(Q,E) with the resolution.
    convolved2: Nexus file containing the convolution of the simulated S(Q,E) with the resolution for FF1*1.01
    assembled: output Nexus file containing the assembled S(Q,E) of the beamline model and the simulated S(Q,E)
    expdata: Optional, experimental nexus file. If passed, output convolved will be binned as expdata.
    costfile: Optional, file to store cost. If passed, residuals and (optionally) partial derivatives will be stored
    derivdata: Optional, perform analytic derivatives (store in costfile if provided)
    derivexclude: list of fitting parameters for which partial derivatives will not be computed
    doshift: Optional, perform the shift of the model function

  Returns:
    wsm: workspace containing the assembled S(Q,E)
    gradients: dictionary of partial derivatives with respect to model parameters
  """
  import numpy
  from copy import copy,deepcopy
  from mantid.simpleapi import (LoadNexus, ScaleX, ConvertToPointData, SaveNexus, DakotaChiSquared, AddSampleLog)

  def shiftalongX(*kargs,**kwargs):
    """ Function to do the shift along the E-axis. By default, does nothing """
    pass
  import interpX
  if doshift: # replace the dummy function with the real thing
    if doshift in dir(interpX):
      shiftalongX=getattr(__import__('interpX'), doshift)
    else:
      shiftalongX = getattr(__import__('interpX'), 'itp_simple')

  def computemodel(p,wse,wsc):
    """Assemble the model
    Arguments
      p: dictionary with parameter values
      wse: Mantid workspace holding the elastic line
      wsc: Mantid workspace holding the convolution of the resolution and the simulation
    Returns:
      wsm: Mantid workspace holding the resulting model
    """
    from mantid.simpleapi import CloneWorkspace
    wsm=CloneWorkspace(wsc)
    E=wse.readX(0) # energy values, bins boundary values
    Eshifted=(E[1:]+E[:-1])/2 # energy values, center bin values
    for i in range(wsc.getNumberHistograms()):
      elastic=wse.readY(i)   # elastic spectrum at a given Q
      convolved=wsc.readY(i) # convolved spectrum at a given Q
      wsm.setY(i, p['b0']+p['b1']*Eshifted + p['e0.'+str(i)]*elastic + p['c0']*convolved) # overwrite spectrum
    return wsm

  # init list of parameters names for which analytical derivative exists, same order as in the input model file
  derivparnames=[] # filled only if derivdata different than None
  p={}
  for pair in open(model,'r').readline().split(';'):
    key,val=[x.strip() for x in pair.split('=')]
    if derivdata and key not in derivexclude: derivparnames.append(key)
    p[key]=float(val)

  # read various inputs
  wsr=LoadNexus(Filename=resolution,OutputWorkspace='resolution')
  wse=ScaleX(InputWorkspace=wsr, OutputWorkspace='elastic',factor=-1) # elastic line
  wsc=LoadNexus(Filename=convolved,OutputWorkspace='convolved')
  E=wsr.readX(0) # energy values, bins boundary values
  de=E[1]-E[0]   # assume all bins have same bin width
  Eshifted=(E[1:]+E[:-1])/2 # energy values, center bin values
  nhist=wsc.getNumberHistograms()
  nrsl=len(Eshifted)*nhist # number of residuals

  # calculate partial numerical derivative with respect to eshift 
  gradients={}
  if 'eshift' in derivparnames: 
    wsm=computemodel(p,wse,wsc)
    eshiftderiv=(shiftalongX(wsm,p['eshift']+0.5*de,newWorkspace='wsplus') - shiftalongX(wsm,p['eshift']-0.5*de,newWorkspace='wsminus')) / de # forward-backward difference with a 0.5*de step
    gradients['eshift']=numpy.zeros(0)
    for i in range(eshiftderiv.getNumberHistograms()): gradients['eshift'] = numpy.concatenate([gradients['eshift'], eshiftderiv.readY(i)])

  # do eshift of component workspaces
  if doshift: Eshifted-=p['eshift']
  wse=shiftalongX(wse,p['eshift']) # shift the spectrum, does nothing if shiftalongX is the dummy function
  wsc=shiftalongX(wsc,p['eshift']) # shift the spectrum, does nothing if shiftalongX is the dummy function

  # find difference in convolutions with FF1 changed
  if convolved2:
    derivparnames.append('FF1')
    # difference in FF1 workspaces
    wsc2=LoadNexus(Filename=convolved2,OutputWorkspace='convolved2')
    wksp_diff=wsc2-wsc
 
  # calculate analytic partial derivatives with respect to the fit parameters
  if derivparnames:
    gradients['b0']=numpy.ones(nrsl)
    gradients['b1']=numpy.zeros(0)
    gradients['c0']=numpy.zeros(0)
    gradients['FF1']=numpy.zeros(0)
    for i in range(nhist):
      gradients['b1'] = numpy.concatenate([gradients['b1'], Eshifted])
      gradients['c0'] = numpy.concatenate([gradients['c0'], wsc.readY(i)])
      if convolved2:
        gradients['FF1'] = numpy.concatenate([gradients['FF1'], wksp_diff.readY(i)])
      gradients['e0.'+str(i)]=numpy.zeros(0)
      for j in range(nhist):
        if i==j: 
          gradients['e0.'+str(i)] = numpy.concatenate([gradients['e0.'+str(i)], wse.readY(i)])
        else:
          gradients['e0.'+str(i)] = numpy.concatenate([gradients['e0.'+str(i)], numpy.zeros(len(Eshifted))])

  if convolved2:
    FF1_1=wsc.getRun().getLogData('FF1').value
    FF1_2=wsc2.getRun().getLogData('FF1').value
    print "FF1 parameters in convolved files ",FF1_2,FF1_1
    gradients['FF1'] *= p['c0']/(FF1_2-FF1_1)

  # save model to file
  wsm=computemodel(p,wse,wsc)
  # add all parameters to assembled file
  for pair in open(model,'r').readline().split(';'):
    key,val=[x.strip() for x in pair.split('=')]
    AddSampleLog(Workspace=wsm,LogName=key,LogText=str(p[key]),LogType='Number')
  SaveNexus(InputWorkspace=wsm, Filename=assembled)

  # save residuals and partial derivatives
  buf=''
  if expdata and costfile:
    wex=LoadNexus(Filename=expdata,OutputWorkspace='experiment')
    chisq,wR=DakotaChiSquared(DataFile=expdata,CalculatedFile=assembled,OutputFile=costfile,ResidualsWorkspace='wR')
    Xe=numpy.zeros(0) # list of errors for each residual
    for i in range(nhist):
      Xe = numpy.concatenate([Xe, wex.readE(i)])
      Ry=wR.readY(i)
      for j in range(len(Ry)):
        buf+=str(Ry[j])+" least_sq_term_"+str(i*len(Ry)+j+1)+"\n"
    for parname in derivparnames: gradients[parname]/=numpy.where(Xe>0,Xe,1) # divide by experimental error (with non-positive elements replaced by one)
    if derivparnames:
      for i in range(nrsl):
        buf+="["
        for parname in derivparnames: buf+=" %.10e"%(-gradients[parname][i])
        buf+=" ]\n"
    open(costfile,'w').write(buf)

  return {'model':wsm, 'gradients':gradients}

def modelBEC_EC(model, resolution, convolved, qvalues, assembled, expdata=None, costfile=None):
  """Assemble the Background, Elastic line and Convolution of the resolution with the simulated S(Q,E)
  This is a hard-coded model consisting of a linear background, and elastic line, and a convolution:
    b0+b1*E  +  +EC(Q)*e0*exp(-e1*Q^2)*Elastic(E)  +  EC(Q)*c0*Resolution(E)xSimulated(Q,E)
    We load Resolution(E)xSimulated(Q,E) as Convolved(Q,E)
    EC(Q) is a fit to the Q-dependence of the integrated intensity of the empty can
    EC(Q) = 2.174495971 - 2.065826056*Q + 0.845367259*Q^2
    
  Arguments:
    model: beamline model file is a single line, e.g,
           b0=1.3211; b1=0.00 e0=0.99; e1=1.9; c0=2.3
    resolution: Nexus file containing the resolution. This will be used to produce a elastic line.
    convolved: Nexus file containing the convolution of the simulated S(Q,E) with the resolution.
    qvalues: single-column file containing list of Q-values
    assembled: output Nexus file containing the assembled S(Q,E) of the beamline model and the simulated S(Q,E)
    expdata: Optional, experimental nexus file. If passed, output convolved will be binned as expdata.
    costfile: Optional, file to store cost. If passed, the cost of comparing convolved and expdata will be saved.

  Returns:
    workspace containing the assembled S(Q,E)
  """
  import numpy
  from mantid.simpleapi import (LoadNexus, ScaleX, ConvertToPointData, SaveNexus, DakotaChiSquared)
  EC = lambda Q: 2.174495971 - 2.065826056*Q + 0.845367259*Q*Q
  Q=[float(q) for q in open(qvalues,'r').read().split('\n')]
  p={}
  for pair in open(model,'r').readline().split(';'):
    key,val=pair.split('=')
    p[key.strip()]=float(val.strip())
  wsr=LoadNexus(Filename=resolution,OutputWorkspace='resolution')
  wsr=ConvertToPointData(wsr)
  E=wsr.readX(0)
  wse=ScaleX(InputWorkspace=wsr, OutputWorkspace='elastic',factor=-1) # elastic line
  wsc=LoadNexus(Filename=convolved,OutputWorkspace='convolved')
  for i in range(wsc.getNumberHistograms()):
    elastic=wse.readY(i) # elastic spectrum at a given Q
    convolved=wsc.readY(i) # convolved spectrum at a given Q
    wsc.setY(i, p['b0']+p['b1']*E + EC(Q[i])*(p['e0']*numpy.exp(-p['e1']*Q[i])*elastic + p['c0']*convolved) ) # overwrite spectrum
  SaveNexus(InputWorkspace=wsc, Filename=assembled)
  if expdata and costfile:
    DakotaChiSquared(DataFile=assembled,CalculatedFile=expdata,OutputFile=costfile)
  return wsc

def modelB_EC_C(model, resolution, convolved, qvalues, assembled, expdata=None, costfile=None):
  """Assemble the Background, Elastic line and Convolution of the resolution with the simulated S(Q,E)
  This is a hard-coded model consisting of a linear background, and elastic line, and a convolution:
    b0+b1*E  +  +EC(Q)*e0*exp(-e1*Q^2)*Elastic(E)  +  c0*Resolution(E)xSimulated(Q,E)
    We load Resolution(E)xSimulated(Q,E) as Convolved(Q,E)
    EC(Q) is a fit to the Q-dependence of the integrated intensity of the empty can
    EC(Q) = 2.174495971 - 2.065826056*Q + 0.845367259*Q^2
    
  Arguments:
    model: beamline model file is a single line, e.g,
           b0=1.3211; b1=0.00 e0=0.99; e1=1.9; c0=2.3
    resolution: Nexus file containing the resolution. This will be used to produce a elastic line.
    convolved: Nexus file containing the convolution of the simulated S(Q,E) with the resolution.
    qvalues: single-column file containing list of Q-values
    assembled: output Nexus file containing the assembled S(Q,E) of the beamline model and the simulated S(Q,E)
    expdata: Optional, experimental nexus file. If passed, output convolved will be binned as expdata.
    costfile: Optional, file to store cost. If passed, the cost of comparing convolved and expdata will be saved.

  Returns:
    workspace containing the assembled S(Q,E)
  """
  import numpy
  from mantid.simpleapi import (LoadNexus, ScaleX, ConvertToPointData, SaveNexus, DakotaChiSquared)
  EC = lambda Q: 2.174495971 - 2.065826056*Q + 0.845367259*Q*Q
  Q=[float(q) for q in open(qvalues,'r').read().split('\n')]
  p={}
  for pair in open(model,'r').readline().split(';'):
    key,val=pair.split('=')
    p[key.strip()]=float(val.strip())
  wsr=LoadNexus(Filename=resolution,OutputWorkspace='resolution')
  wsr=ConvertToPointData(wsr)
  E=wsr.readX(0)
  wse=ScaleX(InputWorkspace=wsr, OutputWorkspace='elastic',factor=-1) # elastic line
  wsc=LoadNexus(Filename=convolved,OutputWorkspace='convolved')
  for i in range(wsc.getNumberHistograms()):
    elastic=wse.readY(i) # elastic spectrum at a given Q
    convolved=wsc.readY(i) # convolved spectrum at a given Q
    wsc.setY(i, (p['b0']+p['b1']*E) + (EC(Q[i])*p['e0']*numpy.exp(-p['e1']*Q[i])*elastic) + (p['c0']*convolved) ) # overwrite spectrum
  SaveNexus(InputWorkspace=wsc, Filename=assembled)
  if expdata and costfile:
    DakotaChiSquared(DataFile=assembled,CalculatedFile=expdata,OutputFile=costfile)
  return wsc

def modelBEC(model, resolution, convolved, qvalues, assembled, expdata=None, costfile=None):
  """Assemble the Background, Elastic line and Convolution of the resolution with the simulated S(Q,E)
  This is a hard-coded model consisting of a linear background, and elastic line, and a convolution:
    b0+b1*E  +  e0*exp(-e1*Q^2)*Elastic(E)  +  c0*Resolution(E)xSimulated(Q,E)
    We load Resolution(E)xSimulated(Q,E) as Convolved(Q,E)
    
  Arguments:
    model: beamline model file is a single line, e.g,
           b0=1.3211; b1=0.00 e0=0.99; e1=1.9; c0=2.3
    resolution: Nexus file containing the resolution. This will be used to produce a elastic line.
    convolved: Nexus file containing the convolution of the simulated S(Q,E) with the resolution.
    qvalues: single-column file containing list of Q-values
    assembled: output Nexus file containing the assembled S(Q,E) of the beamline model and the simulated S(Q,E)
    expdata: Optional, experimental nexus file. If passed, output convolved will be binned as expdata.
    costfile: Optional, file to store cost. If passed, the cost of comparing convolved and expdata will be saved.

  Returns:
    workspace containing the assembled S(Q,E)
  """
  import numpy
  from mantid.simpleapi import (LoadNexus, ScaleX, ConvertToPointData, SaveNexus, DakotaChiSquared)
  Q=[float(q) for q in open(qvalues,'r').read().split('\n')]
  p={}
  for pair in open(model,'r').readline().split(';'):
    key,val=pair.split('=')
    p[key.strip()]=float(val.strip())
  wsr=LoadNexus(Filename=resolution,OutputWorkspace='resolution')
  wsr=ConvertToPointData(wsr)
  E=wsr.readX(0)
  wse=ScaleX(InputWorkspace=wsr, OutputWorkspace='elastic',factor=-1) # elastic line
  wsc=LoadNexus(Filename=convolved,OutputWorkspace='convolved')
  for i in range(wsc.getNumberHistograms()):
    elastic=wse.readY(i) # elastic spectrum at a given Q
    convolved=wsc.readY(i) # convolved spectrum at a given Q
    wsc.setY(i, (p['b0']+p['b1']*E) + (p['e0']*numpy.exp(-p['e1']*Q[i])*elastic) + (p['c0']*convolved) ) # overwrite spectrum
  SaveNexus(InputWorkspace=wsc, Filename=assembled)
  if expdata and costfile:
    DakotaChiSquared(DataFile=assembled,CalculatedFile=expdata,OutputFile=costfile)
  return wsc

def modelBEC1Q(model, resolution, convolved, qvalues, assembled, expdata=None, costfile=None):
  """Assemble the Background, Elastic line and Convolution of the resolution with the simulated S(Q,E)
  This is a hard-coded model consisting of a linear background, and elastic line, and a convolution:
    b0+b1*E  +  1/Q*e0**Elastic(E)  +  c0*Resolution(E)xSimulated(Q,E)
    We load Resolution(E)xSimulated(Q,E) as Convolved(Q,E)
  Note the 1/Q dependence which is used to simulate the Q-dependence of the signal for a normalized
  empty can in BASIS at room temperature

  Arguments:
    model: beamline model file is a single line, e.g,
           b0=1.3211; b1=0.00 e0=0.09; c0=2.3
    resolution: Nexus file containing the resolution. This will be used to produce a elastic line.
    convolved: Nexus file containing the convolution of the simulated S(Q,E) with the resolution.
    qvalues: single-column file containing list of Q-values
    assembled: output Nexus file containing the assembled S(Q,E) of the beamline model and the simulated S(Q,E)
    expdata: Optional, experimental nexus file. If passed, output convolved will be binned as expdata.
    costfile: Optional, file to store cost. If passed, the cost of comparing convolved and expdata will be saved.

  Returns:
    workspace containing the assembled S(Q,E)
  """
  import numpy
  from mantid.simpleapi import (LoadNexus, ScaleX, ConvertToPointData, SaveNexus, DakotaChiSquared)
  Q=[float(q) for q in open(qvalues,'r').read().split('\n')]
  p={}
  for pair in open(model,'r').readline().split(';'):
    key,val=pair.split('=')
    p[key.strip()]=float(val.strip())
  wsr=LoadNexus(Filename=resolution,OutputWorkspace='resolution')
  wsr=ConvertToPointData(wsr)
  E=wsr.readX(0)
  wse=ScaleX(InputWorkspace=wsr, OutputWorkspace='elastic',factor=-1) # elastic line
  wsc=LoadNexus(Filename=convolved,OutputWorkspace='convolved')
  for i in range(wsc.getNumberHistograms()):
    elastic=wse.readY(i) # elastic spectrum at a given Q
    convolved=wsc.readY(i) # convolved spectrum at a given Q
    wsc.setY(i, (p['b0']+p['b1']*E) + (1/Q[i]*p['e0']*elastic) + (p['c0']*convolved) ) # overwrite spectrum
  SaveNexus(InputWorkspace=wsc, Filename=assembled)
  if expdata and costfile:
    DakotaChiSquared(DataFile=assembled,CalculatedFile=expdata,OutputFile=costfile)
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
  p=argparse.ArgumentParser(description='Provider for services involving convolution of simulated S(Q,E) with a model beamline. Available services are: lowTresolution, modelBEC, modelB_EC_C, modelB_freeE_C.')
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
    p.add_argument('--expdata',help='optional, experimental nexus file. If passed, output convolved will be binned as expdata.')
    p.add_argument('--costfile',help='optional, file to store cost. If passed, the cost of comparing convolved and expdata will be saved.')
    if '-explain' in sys.argv:
      p.parse_args(args=('-h',))
    else:
      args=p.parse_args()
      modelBEC(args.model, args.resolution, args.convolved, args.qvalues, args.assembled, args.expdata, args.costfile)
  elif 'modelB_EC_C' in sys.argv:
    p.description='Assemble the background, elastic line and convolution of the resolution with the simulated S(Q,E) according to model (b0+b1*E  +  EC(Q)*e0*exp(-e1*Q^2)*Elastic(E)  +  c0*Resolution(E)xSimulated(Q,E)). EC(Q) is the modeled Q-dependence of the integrated intensity for an empty can in BASIS. Output to a Nexus file'
    for action in p._actions:
      if action.dest=='service': action.help='substitue "service" with "modelBEC"' # update help message
    p.add_argument('--model',help='name of the file containing the model beamline string')
    p.add_argument('--resolution',help='name of the nexus file containing the resolution function. This will be used to produce an elastic line.')
    p.add_argument('--convolved',help='Nexus file containing the convolution of the simulated S(Q,E) with the resolution.')
    p.add_argument('--qvalues',help='Single-column file containing list of Q-values.')
    p.add_argument('--assembled',help='output Nexus file containing the assembled S(Q,E) of the beamline model and the simulated S(Q,E)')
    p.add_argument('--expdata',help='optional, experimental nexus file. If passed, output convolved will be binned as expdata.')
    p.add_argument('--costfile',help='optional, file to store cost. If passed, the cost of comparing convolved and expdata will be saved.')
    if '-explain' in sys.argv:
      p.parse_args(args=('-h',))
    else:
      args=p.parse_args()
      modelB_EC_C(args.model, args.resolution, args.convolved, args.qvalues, args.assembled, args.expdata, args.costfile)
  elif 'modelBEC_EC' in sys.argv:
    p.description='Assemble the background, elastic line and convolution of the resolution with the simulated S(Q,E) according to model b0+b1*E + EC(Q)(e0*exp(-e1*Q^2)*Elastic(E) + c0*Resolution(E)xSimulated(Q,E)). EC(Q) is the modeled Q-dependence of the integrated intensity for an empty can in BASIS. Output to a Nexus file'
    for action in p._actions:
      if action.dest=='service': action.help='substitue "service" with "modelBEC"' # update help message
    p.add_argument('--model',help='name of the file containing the model beamline string')
    p.add_argument('--resolution',help='name of the nexus file containing the resolution function. This will be used to produce an elastic line.')
    p.add_argument('--convolved',help='Nexus file containing the convolution of the simulated S(Q,E) with the resolution.')
    p.add_argument('--qvalues',help='Single-column file containing list of Q-values.')
    p.add_argument('--assembled',help='output Nexus file containing the assembled S(Q,E) of the beamline model and the simulated S(Q,E)')
    p.add_argument('--expdata',help='optional, experimental nexus file. If passed, output convolved will be binned as expdata.')
    p.add_argument('--costfile',help='optional, file to store cost. If passed, the cost of comparing convolved and expdata will be saved.')
    if '-explain' in sys.argv:
      p.parse_args(args=('-h',))
    else:
      args=p.parse_args()
      modelBEC_EC(args.model, args.resolution, args.convolved, args.qvalues, args.assembled, expdata=args.expdata, costfile=args.costfile)
  elif 'modelB_freeE_C' in sys.argv:
    p.description='Assemble the background, elastic line and convolution of the resolution with the simulated S(Q,E) according to model b0+b1*E + e0(Q)*Elastic(E) + c0*Resolution(E)xSimulated(Q,E)). e0(Q) is a set of fitting parameters, one for each Q. Output to a Nexus file.'
    for action in p._actions:
      if action.dest=='service': action.help='substitue "service" with "modelB_freeE_C"' # update help message
    p.add_argument('--model',        help='name of the file containing the model beamline string')
    p.add_argument('--resolution',   help='name of the nexus file containing the resolution function. This will be used to produce an elastic line.')
    p.add_argument('--convolved',    help='Nexus file containing the convolution of the simulated S(Q,E) with the resolution.')
    p.add_argument('--convolved2',    help='Nexus file containing the convolution of the simulated S(Q,E) with the resolution for FF1*0.01.')
    p.add_argument('--qvalues',      help='Single-column file containing list of Q-values.')
    p.add_argument('--assembled',    help='output Nexus file containing the assembled S(Q,E) of the beamline model and the simulated S(Q,E)')
    p.add_argument('--expdata',      help='optional, experimental nexus file. If passed, output convolved will be binned as expdata.')
    p.add_argument('--costfile',     help='optional, file to store cost. If passed, the cost of comparing convolved and expdata will be saved.')
    p.add_argument('--derivdata',    help='optional, set to 1 if to perform analytic derivatives (store in costfile if provided)')
    p.add_argument('--derivexclude', help='optional, string containing space-separated parameters for which partial derivatives will not be computed')
    p.add_argument('--doshift',      help='optional, perform the shift of the model function')
    if '-explain' in sys.argv:
      p.parse_args(args=('-h',))
    else:
      args=p.parse_args()
      derivexclude=[]
      if args.derivexclude: derivexclude=args.derivexclude.split()
      modelB_freeE_C(args.model, args.resolution, args.convolved, args.convolved2, args.assembled, expdata=args.expdata, costfile=args.costfile, derivdata=bool(args.derivdata), derivexclude=derivexclude, doshift=args.doshift)
  else:
    print 'service not found'
