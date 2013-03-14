'''
Created on Mar 12, 2013

  Classes in variables module mimic the hierarchy of classes for Dakota variables
  through the use of domain subclasses. The purpose of this module is to offer
  an interface to read and write to the 'variables' section of the Dakota inputs file.

@author: jmborr
'''
import logging
from copy import deepcopy

logger = logging.getLogger(__name__)

# Different Dakota variable types. The order is critical
dakotatypes=['continuous_design',
             'discrete_design_range',
             'discrete_design_set_int',
             'discrete_design_set_real',
             'normal_uncertain',
             'lognormal_uncertain',
             'uniform_uncertain',
             'loguniform_uncertain',
             'triangular_uncertain',
             'exponential_uncertain',
             'beta_uncertain',
             'gamma_uncertain',
             'gumbel_uncertain',
             'frechet_uncertain',
             'weibull_uncertain',
             'histogram_bin_uncertain',
             'poisson_uncertain',
             'binomial_uncertain',
             'negative_binomial_uncertain',
             'geometric_uncertain',
             'hypergeometric_uncertain',
             'histogram_point_uncertain',
             'interval_uncertain',
             'continuous_state',
             'discrete_state_range',
             'discrete_state_set_int',
             'discrete_state_set_real'
             ]

# Properties for each Dakota type
propertynames={'continuous_design':['initial_state','lower_bounds','upper_bounds','descriptors'],
               'discrete_design_range':['initial_point','lower_bounds','upper_bounds','descriptors'],
               'discrete_design_set_int':[],
               'discrete_design_set_real':[],
               'normal_uncertain':['means','std_deviations','descriptors'],
               'lognormal_uncertain':[],
               'uniform_uncertain':['lower_bounds','upper_bounds','descriptors'],
               'loguniform_uncertain':[],
               'triangular_uncertain':[],
               'exponential_uncertain':[],
               'beta_uncertain':[],
               'gamma_uncertain':[],
               'gumbel_uncertain':[],
               'frechet_uncertain':[],
               'weibull_uncertain':[],
               'histogram_bin_uncertain':[],
               'poisson_uncertain':[],
               'binomial_uncertain':[],
               'negative_binomial_uncertain':[],
               'geometric_uncertain':[],
               'hypergeometric_uncertain':[],
               'histogram_point_uncertain':[],
               'interval_uncertain':[],
               'continuous_state':['initial_state','descriptors'],
               'discrete_state_range':['initial_state','lower_bounds','upper_bounds','descriptors'],
               'discrete_state_set_int':['initial_state','set_values','descriptors'],
               'discrete_state_set_real':[]
               }

def rank_dakota_type(dakotatype):
  """returns the index of string dakotatype in the list dakotatypes"""
  return dakotatypes.index[dakotatype]
  
class Domain(object):
  """Base class for domains associated with a variable
  
  Attributes:
    dakotatype: string defined for each domain subclass
  """

  def __init__(self):
    self._values=None
    self.dakotatype=None

  def getvalues(self):
    return self._values

  def setvalues(self,values):
    self._values=values

  def copyvalues(self,values):
    self._values=deepcopy(values)

  def get_dakota_type(self):
    return self.dakotatype

  def getproperties(self):
    return {}

class DomainCRSD:
  """Class for a Continuous Real Single Dimension domain
  
  The Domain is defined by the bounds of a segment in real space
  """ 

  def __init__(self,start,end):
    self.set_bounds(start, end)
    self.dakotatype='continuous_design'

  def get_bounds(self):
    return self._values

  def set_bounds(self,start,end):
    if isinstance(start,float) and isinstance(end,float) and start<end:
      self.values=[start,end]
    else:
      logger.error("Incorrect types and/or incorrect ordering of bounds")

  def getproperties(self):
    return {'lower_bounds':self._values[0], 'upper_bounds':self._values[1]}

class Variable(object):
  """Class for reading and writing Dakota variables"""

  def __init__(self,descriptor):
    self.descriptor=descriptor
    self._initial=None # stores the state of the variable
    self._domain=None # boundaries for the allowed states of the variable

  def domainChecks(self,domain):
    """Check if domain type is OK. Override with subclass method"""
    return True

  def copydomain(self,domain):
    if self.domainChecks(domain): self._domain=deepcopy(domain)

  def setdomain(self,domain):
    if self.domainChecks(domain): self._domain=domain

  def get_dakota_type(self):
    return self._domain.get_dakota_type()

  def dakota_type_rank(self):
    return dakotatypes.index[self.get_dakota_type()]

  def __lt__(self,right):
    if self.dakota_type_rank()<right.dakota_type_rank(): return True
    return False

  def getStateProperties(self):
    """Properties related to the state of the variable.
     Override with subclass method"""
  return {}

  def getproperties(self):
    """The properties of a variable are the union of its name, the state
    of the variable, and the boundaries for the variable""" 
    return {'descriptors':self.descriptor}+self.getStateProperties()+self._domain.getproperties()

  def read_dakota(self,filehandle):
    pass

  def write_dakota(self,filehandle):
    self._domain.write_dakota(filehandle)
    pass


class VariableCRSD(Variable):
  """Class for a Continuous Real Single Dimension variable.
  Only admits domains of class DomainCRSD"""

  def domainChecks(self,domain):
    """Domain type must be of certain type.
    Overrides parent method"""
    if type(domain).__name__=='DomainCRSD': return True
    return False

  def getStateProperties(self):
    """Properties related to the state of the variable.
    Overrides parent method"""
    return {'initial_state':self._initial}

class VariableHomogeneousSet(object):
  """Class to gather a collection of Variable objects of the same Dakota type"""

  def __init__(self,dakotatype):
    if dakotatype in dakotatypes:
      self.dakotatype=dakotatype
    self._variables=[]

  def get_dakota_type(self):
    return self.dakotatype

  def insert(self,variable):
    if variable.get_dakota_type==self.get_dakota_type():
      self._variables.append(variable)

  def merge(self,hset):
    """merge another homogeneous set into itself"""
    if self.dakotatype==hset.dakotatype:
      self._variables += hset._variables

  def size(self):
    return len(self._variables)

  def propertynames(self):
    return propertynames(self.dakotatype)

  def writeToString(self):
    """Write a block of properties and values for the set
    
    Example: The output of a homogeneous block containing two variables
    of type VariableCRSD with names 'radius' and 'location' could be:
      s = 'continuous_design = 2
          initial_point 0.9 1.1
          upper_bounds 5.8 2.9
          lower_bounds 0.5 -2.9
          descriptors 'radius' 'location''
    """
    s=self.dakotatype+' = '+str(self.size())+'\n'
    buf={}
    for prop in self.propertynames(): buf[prop]='' 
    for variable in self._variables:
      for prop,value in variable.getproperties().items():
        if isinstance(value,str): value="'"+value+"'" # Dakota needs enclosing of strings
        buf[prop] += str(value)+' '
    for prop in self.propertynames(): s+=buf[prop]+'\n'
    return s

  def writeToFile(self,fhandle):
    fhandle.write(self.writeToString())

class VariableSet(object):
  """Class to gather a collection of Variable objects into a set"""

  def __init__(self,identifier):
    self.identifier=identifier
    self._homogeneous=[]

  def size(self):
    s=0
    for hset in self._homogeneous: s+=hset.size()
    return s

  def get_dakota_types(self):
    """List of Dakota types"""
    return [h.get_dakota_type() for h in self.homogeneous]

  def has_dakota_type(self, dakotatype):
    """Check if homogeneneous set with passed Dakota type exists"""
    if dakotatype in self.get_dakota_types(): return True
    return False

  def getHomogeneousSet(self,dakotatype):
    """Returns handle to the homogeneous set with same Dakota type"""
    for hset in self._homogeneous:
      if hset.get_dakota_type()==dakotatype: return hset
    return None

  def insertHomogeneousSet(self,hset):
    """Insert a homogeneous set taking care of the order. Merge if already exists a
    homogeneous set with same Dakota type"""
    dakotatype=hset.get_dakota_type()
    if self.has_dakota_type(dakotatype):
      self.getHomogeneousSet(dakotatype).merge(hset)
    else:
      rank=rank_dakota_type(dakotatype)
      index=0
      for dtype in self.get_dakota_types():
        if rank>rank_dakota_type(dtype):break
        index+=1
      self._homogeneous.insert(index,hset)

  def insertVariable(self,variable):
    """Push a Variable object in the list. Create a new homogeneous set if needed"""
    dakotatype=variable.get_dakota_type()
    if self.has_dakota_type(dakotatype): # insert variable into appropriate set
      self.getHomogeneousSet(dakotatype).insert(variable)
    else: # create new homogeneous set with the variable and insert the set
      hset=VariableHomogeneousSet(dakotatype)
      hset.insert(variable)
      self.insertHomogeneousSet(hset)
    pass

  def writeToString(self):
    """Write the variables section for a Dakota file
    """
    s=''
    if self.identifier: s+="id_variables = '"+self.identifier+"'\n" # Dakota needs enclosing of strings
    for hset in self._homogeneous:
      s+=hset.writeToString()+'\n'
    return self

  def writeToFile(self,fhandle):
    fhandle.write(self.writeToString())