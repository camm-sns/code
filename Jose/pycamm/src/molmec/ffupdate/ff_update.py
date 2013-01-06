from pdb import set_trace as trace  # only for interactive debugging purposes

import sys
import re
import argparse

from molmec.fftpl.psf import FFParam

def loadFFtpl(fftpl_file):
  """From the XML file containing the list of FFParam objects
  and the force-field template file, load these items
  """
  from xml.etree.ElementTree import parse
  root = parse(fftpl_file).getroot()
  params=[]
  for ff_param in root.find('FFParams'):
    x=FFParam()
    params.append(x.fromElementTreeElement(ff_param))
  template=root.find('FFTemplate').text
  return params,template

def getParams(paramsFile):
  """Load the params file from Dakota onto a standard dictionary"""
  from itertools import islice
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

def updateTemplate(template,params):
  """ Insert actual values for the parameters in the template.
  The formatting to insert the values is contained in the template.
  Example: _FF1_(%-14.6) indicates substitute parameter FF1 with its
  current value with a C-style format of %-14.6.
  """
  for param in params:
    cformats=re.findall("_%s_"%param._name+'\((\%\-\w+\.\w+)\)',template)
    cformats=list(set(cformats)) # Remove duplicates
    for cformat in cformats:
      template=template.replace("_%s_(%s)"%(param._name,cformat), cformat%param._value)
  return template

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='script generating updated force field')
  parser.add_argument('--dak',help='name of the dakota params file')
  parser.add_argument('--fftpl',help='force field template, Ex: --fftpl=fftpl.xml')
  parser.add_argument('--ffout',help='name of the output force field. Ex: --ffout=ff.psf')
  args = parser.parse_args()

  dakota_vals = getParams(args.dak) # read in Dakota params file
  params,template=loadFFtpl(args.fftpl) # read in force field template file
  
  free_params=[param for param in params if param.isFree()]
  for param in free_params: param._value=dakota_vals[param._name] # Update free param values
  for param in params:
    if not param.isFree(): param.resolveConstraint(free_params) # Update non-free param values
  template=updateTemplate(template,params)
  open(args.ffout,'w').write(template)
  sys.exit(0)

