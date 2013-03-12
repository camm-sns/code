'''
Script to generate a force field template from a CHARMM or NAMD 
psf topology file.

Substitute charges with keywords

'''
#from pdb import set_trace as trace  # only for interactive debugging purposes
import logging
logger = logging.getLogger("Molmec.fftpl.PSF")

class PSFParseError(Exception):
  """Signifies an error during parsing of the PSF file"""
  pass

class FFParam(object):
  """ Encapsulate properties of a force field parameter """
  def __init__(self,name=None):
    self._name=None
    if name: self._name=name
    self._tie=None #initialized as free parameter
    self._value=None
    self._init=None
    self._minimum=None
    self._maximum=None
    self._tolerance=None
    return None

  def setValue(self,value):
    self._value=value

  def isFree(self):
    if self._tie:
      return False
    return True

  def __setattr__(self, key, val):
    """ Overload to ensure correct type assignment"""
    need_type_fix=('_value','_init','_minimum','_maximum','_tolerance')
    if val and key in need_type_fix:
      self.__dict__[key]=float(val)
    else:
      self.__dict__[key]=val
  
  def resolveTie(self,free_params):
    """ Assign value based on the tie expression """
    if not self.isFree():
      tie=self._tie
      for param in free_params:
        tie=tie.replace(param._name,str(param._value))
      self._value=eval(tie)
    return self._value

  def toElementTreeElement(self):
    """save as xml.ElementTree.Element object"""
    from xml.etree.ElementTree import Element
    el=Element(self.__class__.__name__)
    for attribute in vars(self):
      if attribute[0]=='_':
        value=self.__getattribute__(attribute)
        if value: el.attrib[attribute[1:]]=str(value)
    return el

  def fromElementTreeElement(self, el):
    """ read from xml.ElementTree.Element object.
    Overloaded __setattr__ takes care of assigning the correct types
    """
    #trace()
    valid_keys=vars(self).keys()
    for key,value in el.attrib.items():
      if '_'+key in valid_keys:
        self.__setattr__('_'+key, value)
    return self

def initFFParams(conf_file):
  """ Parse the parameter configuration file that specifies the force field
  parameters to be fit
  
  Example configuration file:
  #name, tie, iatom, extend, minimum, init, maximum, tolerance
  FF1, , 930, 1, 0.30, 0.45, 0.60, 0.01
  FF2, 2*FF1, 931, 1
  
  FF1 is a free parameter, thus it has no tie.
  FF2 is a non-free parameter, since is twice FF1. Thus, the minimum, init,
  maximum, and tolerance values are defined by the tie and there is no
  need to specify those in the configuration file.
  
  FF1 is applicable to atom iatom=930. Furthermore, FF1 is applicable to atoms
  analogous to 931, as declared by extend=1.
   """
  cfile=open(conf_file,'r')
  cfile.readline() #skip over the initial comment
  params={}
  for line in cfile.readlines():
    fields=[x.strip() for x in line.split(',')]
    name,tie=fields[0:2]
    if name not in params.keys():
      p=FFParam(name)
      if not tie: #free parameter
        minimum,init,maximum,tolerance=[float(x) for x in fields[4:9]]
        p._minimum=minimum
        p._init=init
        p._maximum=maximum
        p._tolerance=tolerance
      else:
        p._tie=tie
      params[name]=p
  return params

def initSeedAtomList(conf_file, atom_list):
  """output the atoms that will serve to compare
  their types to other atoms"""
  cfile=open(conf_file,'r')
  cfile.readline() #skip over the initial comment
  seed_list=[]
  for line in cfile.readlines():
    if line[0]=='#' or not line.strip(): continue # avoid comment and blank lines
    fields=[x.strip() for x in line.split(',')]
    name=fields[0]
    iatom=int(fields[2])-1
    extend=int(fields[3])
    for atom in atom_list:
      if atom.number==iatom:
        seed_list.append((atom,name,extend))
        break
  return seed_list

def resolvePSFformat(psf_file):
  """which format is the PSF file?"""
  psffile = open(psf_file,'r')
  header=psffile.readline()
  if header[:3] != "PSF":
    logger.error("%s is not valid PSF file (header = %r)", psffile.name, header)
    raise PSFParseError("%s is not a valid PSF file" % psffile.name)
  header_flags = header[3:].split()
  psf_format = "STANDARD"    # CHARMM
  if "NAMD" in header_flags:
    psf_format = "NAMD"        # NAMD/VMD
  elif "EXT" in header_flags:
    psf_format = "EXTENDED"    # CHARMM
  return psf_format

def parsePSF(psf_file):
  """parse the topology file"""
  from MDAnalysis.topology.PSFParser import parse
  atom_list=parse(psf_file)['_atoms'] #list of MDAnalysis.core.AtomGroup.Atom objects
  #store the atom lines
  prelines='' # lines of the topology file before the atom lines
  atom_lines=[] # store the atom lines
  suflines='' # lines of the topology file after the atom lines
  pf=open(psf_file,'r')
  line=pf.readline()
  prelines += line
  while '!NATOM' not in line: 
    line=pf.readline()
    prelines += line
  nlines=int(line.split()[0])
  iline=0
  while iline<nlines: 
    atom_lines.append(pf.readline())
    iline +=1
  while line:
    suflines+=line
    line=pf.readline()
  return [atom_list,prelines,atom_lines,suflines]

def isSameType(atom1,atom2):
  """compare types between two atoms. In this case we require that
  the two atoms have same type, residue, and segid"""
  if atom1.segid==atom2.segid:
    if atom1.name==atom2.name:
      if atom1.resname==atom2.resname:
        return True
  return False

def insertFFParmName(line,name,psf_format):
  """replace the charge with the keyword name, with appropriate format"""
  if psf_format=='NAMD':
    items=line.split()
    items[6]='_%s_'%name+'(%f)'
    return ' '.join(items)
  elif psf_format=='EXTENDED':
    return line[0:52]+'_%s_'%name+'(%-14.6f)'+line[66:]
  else:
    return line[0:34]+'_%s_'%name+'(%-14.6f)'+line[48:]
  pass

def insertFFParamsNames(atom_lines,atom_list,seed_list,psf_format='STANDARD'):
  """ Insert force field parameter names where needed """
  buf=''
  for index in range(len(atom_lines)):
    atom1=atom_list[index]
    line=atom_lines[index]
    inserted=False
    #check atom1 is same type than some atom of seed_list
    for (atom2,name,extend) in seed_list:
      if atom1==atom2 or (extend and isSameType(atom1,atom2)):
        buf+=insertFFParmName(line,name,psf_format)
        inserted=True
        break
    if not inserted: buf+=line
  return buf

def generateFFtemplate(params,buf):
  """ generate force field template XML"""
  from xml.etree.ElementTree  import Element,Comment,tostring
  from xml.dom import minidom
  # initialize the root of the document
  root=Element('root')
  comment = Comment('Force field template file')
  root.append(comment)
  # list of force field parameters
  parlist=Element('FFParams')
  for param in params.values():
    el=param.toElementTreeElement()
    parlist.append(el)
  root.append(parlist)
  # a verbatim copy of the force field template
  template=Element('FFTemplate')
  template.text=buf
  root.append(template)
  # pretty print to string
  buf=tostring(root,'utf-8')
  reparsed=minidom.parseString(buf)
  return reparsed.toprettyxml(indent="  ")
  #return minidom.parseString( tostring(root,'utf-8') ).toprettyxml(indent="  ")

if __name__=='__main__':
  from argparse import ArgumentParser
  parser = ArgumentParser(description='script generating force field template')
  parser.add_argument('--ff', help='PSF topology file')
  parser.add_argument('--conf', help='parameter configuration file') #this instead of the future GUI
  parser.add_argument('--fftpl',help='name of the output XML force field template file')
  args = parser.parse_args()

  # atom_list is a list of MDAnalysis.core.AtomGroup.Atom objects
  [atom_list,buf,atom_lines,suflines]=parsePSF(args.ff)
  seed_list=initSeedAtomList(args.conf,atom_list) #list of atoms serving as seed
  buf+=insertFFParamsNames(atom_lines,atom_list,seed_list,
                           psf_format=resolvePSFformat(args.ff))
  buf+=suflines
  params=initFFParams(args.conf) # list of FFParam objects
  buf=generateFFtemplate(params,buf) # write force field template
  open(args.fftpl,'w').write(buf.encode('utf-8'))