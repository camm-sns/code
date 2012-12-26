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

def getParams(resultsFile):
  """Load the results file from Dakota onto a standard dictionary"""
  from itertools import islice
  pf=open(resultsFile)
  # find number of parameters to read
  patt=re.compile('(\d+)\s+variable')
  nparm=int( patt.search(pf.readline()).group() )
  # initialize dictionary containing values for the parameters
  parms={}
  for line in islice(pf,nparm):
    val,name=line.split()
    parms[name]=float(val)
  pf.close()
  return parms

def resolveConstraints(constr_list,mapping):
  """find values for the force field parameters
    using the values of the free parameters and the constraints
    in the force field parameter mapping file.
  """
  for constraint in constr_list:
    for name in mapping.keys():
      constraint=constraint.replace(name,'%s'%mapping[name].value)
    name,sval=constraint.split('=')
    mapping[name].value=eval(sval)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='script generating updated force field')
  parser.add_argument('--dak',help='name of the dakota results file')
  parser.add_argument('--mapf',help='name of the force field mapping file')
  parser.add_argument('--fftpl',help='force field template, Ex: --fftpl=ce1_tpl.psf')
  parser.add_argument('--ffout',help='name of the output force field. Ex: --ffout=ce1.psf')
  args = parser.parse_args()

  dakota_vals = getParams(args.dak) # read Dakota output file
  # read force field mapping file and map to Dakota proposed values
  ceff = open(args.fftpl).read() # read the force field template file

  open(args.ffout,'w').write(ceff) #write updated force field
  sys.exit(0)

