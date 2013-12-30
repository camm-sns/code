from pdb import set_trace as trace  # only for interactive debugging purposes

import sys
import re
import argparse
import csv
import os.path
import shutil

from simulation.src.molmec.fftpl.psf import FFParam

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
  parmstr={}
  for line in islice(pf,nparm):
    val,name=line.split()
    parms[name]=float(val)
    parmstr[name]=val
  pf.close()
  return parms,parmstr

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
  parser.add_argument('--pout',help='name of the output parameter file Ex: --pout=output.csv')
  args = parser.parse_args()

  dakota_vals,dakota_valstr = getParams(args.dak) # read in Dakota params file
  if args.pout is not None:
    data = {}
    if os.path.isfile(args.pout):
      f = open(args.pout)
      r = csv.reader(f)
      for key, val in r:
        data[key] = val
        if val == str(dakota_vals["FF1"]):
          f.close()
          sys.stdout.write(key)
          sys.exit(key)
      f.close()
    data[args.dak.split('in.')[1]] =  dakota_vals["FF1"]
    g = open(args.pout, "w")
    w = csv.writer(g)
    for key, val in data.items():
      w.writerow([key, val])
    g.close()

  fwd_file = open(args.dak+'_1','w')
  old_file = open(args.dak)
  for line in old_file:
      fwd_file.write(line.replace(str(dakota_valstr["FF1"]), str(1.01*dakota_vals["FF1"])))
  fwd_file.close()
  old_file.close()
  bck_file = open(args.dak+'_0','w')
  old_file = open(args.dak)
  for line in old_file:
      bck_file.write(line.replace(str(dakota_valstr["FF1"]), str(0.99*dakota_vals["FF1"])))
  bck_file.close()
  old_file.close()
  params,template=loadFFtpl(args.fftpl) # read in force field template file
  free_params=[param for param in params if param.isFree()]
  for param in free_params: param._value=1.01*dakota_vals[param._name] # Update free param values
  for param in params:
    if not param.isFree(): param.resolveTie(free_params) # Update non-free param values
  template=updateTemplate(template,params)
  ffoutf=args.ffout.replace('.psf','_1.psf')
  open(ffoutf,'w').write(template)

  params,template=loadFFtpl(args.fftpl) # read in force field template file
  free_params=[param for param in params if param.isFree()]
  for param in free_params: param._value=0.99*dakota_vals[param._name] # Update free param values
  for param in params:
    if not param.isFree(): param.resolveTie(free_params) # Update non-free param values
  template=updateTemplate(template,params)
  ffoutb=args.ffout.replace('.psf','_0.psf')
  open(ffoutb,'w').write(template)
  
  params,template=loadFFtpl(args.fftpl) # read in force field template file
  free_params=[param for param in params if param.isFree()]
  for param in free_params: param._value=dakota_vals[param._name] # Update free param values
  for param in params:
    if not param.isFree(): param.resolveTie(free_params) # Update non-free param values
  template=updateTemplate(template,params)
  open(args.ffout,'w').write(template)
  sys.stdout.write(str(args.dak.split('in.')[1]))
  sys.exit(0)

