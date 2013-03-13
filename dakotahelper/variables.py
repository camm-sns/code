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
             'discrete_design_set_integer',
             'discrete_design_set_integer',
             'normal_uncertain',
             'lognormal_uncertain',
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
             'discrete_state_set_integer',
             'discrete_state_set_real'
             ]


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

  def read_dakota(self,filehandle):
    pass

  def write_dakota(self,filehandle):
    pass

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

class Variable(object):
  """Class for reading and writing Dakota variables"""

  def __init__(self,descriptor):
    self.descriptor=descriptor
    self._domain=None
    self._init=None
    self._current=None

  def copydomain(self,domain):
    self._domain=deepcopy(domain)

  def setdomain(self,domain):
    self._domain=domain

  def get_dakota_type(self):
    return self._domain.get_dakota_type()

  def dakota_type_rank(self):
    return dakotatypes.index[self.get_dakota_type()]

  def __lt__(self,right):
    if self.dakota_type_rank()<right.dakota_type_rank(): return True
    return False

  def read_dakota(self,filehandle):
    self._domain.read_dakota(filehandle)

  def write_dakota(self,filehandle):
    self._domain.write_dakota(filehandle)
    pass


class VariableSet(object):
  """Class to gather a collection of of Variable objects into a set"""

  def __init__(self,identifier):
    self.identifier=identifier
    self._variables=[]

  def insert(self,variable):
    """Push a Variable object in the list while preserving the rank of dakota types"""
    if self._variables:
      index=len(self._variables)
      while index>=0 and variable<self._variables[index]:
        index -=1
      index+=1
    self._variables(index,variable)