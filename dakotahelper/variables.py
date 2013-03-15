'''
Created on Mar 12, 2013

  Classes in variables module mimic the hierarchy of classes for Dakota variables
  through the use of domain subclasses. The purpose of this module is to offer
  an interface to read and write to the 'variables' section of the Dakota inputs file.

  This is a typical variables section in a Dakota inputs file (from the Dakota reference manual) 
  variables,
    id_variables = 'V1',
    continous_design = 2
      initial_point   0.9  1.1
      upper_bounds    5.8  2.9
      lower_bounds    0.5  -2.9
      descriptors    'radius'  'location
    discrete_design_range = 1
      initial_point  2
      upper_bounds   1
      lower_bounds   3
      descriptors    'material'
    normal_uncertain = 2
      means            248.89,  593.33
      std_deviations   12.4,  29.7
      descriptors      'TF1n'  'TF2n'
    uniform_uncertain = 2
      lower_bounds    199.3  474.63
      upper_bounds    298.5  712.0
      descriptors     'TF1u'  'TF2u'
    continuous_state = 2
      initial_state = 1.e-4  1.e-6
      descriptors   = 'EPSIT1'  'EPSIT2'
    discrete_state_set_int = 1
      initial_state = 100
      set_values    = 100 212 375
      descriptors   = 'load_case'

@author: jmborr
'''
import logging
from copy import deepcopy

logger = logging.getLogger(__name__)

""" Different Dakota variable types. The order is critical
  Variables Specification from Dakota reference manual
    <continuous design>
    <discrete design range>
    <discrete design set integer>
    <discrete design set real>
    <normal uncertain>
    <lognormal uncertain>
    <uniform uncertain>
    <loguniform uncertain>
    <triangular uncertain>
    <exponential uncertain>
    <beta uncertain>
    <gamma uncertain>
    <gumbel uncertain>
    <frechet uncertain>
    <weibull uncertain>
    <histogram bin uncertain>
    <poisson uncertain>
    <binomial uncertain>
    <negative binomial uncertain>
    <geometric uncertain>
    <hypergeometric uncertain>
    <histogram point uncertain>
    <interval uncertain>
    <continuous state>
    <discrete state range>
    <discrete state set integer>
    <discrete state set real>
"""
dakotatypes=['init_type', # only needed to instantiate empyt objects
             'continuous_design',
             'discrete_design_range',
             'discrete_design_set_integer',
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
             'discrete_state_set_integer',
             'discrete_state_set_real',
             ]

# Properties for each Dakota type
propertynames={'continuous_design':['initial_state','lower_bounds','upper_bounds','scale_types','scales','descriptors'],
               'discrete_design_range':['initial_point','lower_bounds','upper_bounds','descriptors'],
               'discrete_design_set_integer':['initial_point','num_set_values','set_values','descriptors'],
               'discrete_design_set_real':['initial_point','num_set_values','set_values','descriptors'],
               'normal_uncertain':['means','std_deviations','lower_bounds','upper_bounds','descriptors'],
               'lognormal_uncertain':['means','std_deviations','error_factors','lambdas','zetas','lower_bounds','upper_bounds','descriptors'],
               'uniform_uncertain':['lower_bounds','upper_bounds','descriptors'],
               'loguniform_uncertain':['lower_bounds','upper_bounds','descriptors'],
               'triangular_uncertain':['modes','lower_bounds','upper_bounds','descriptors'],
               'exponential_uncertain':['betas','descriptors'],
               'beta_uncertain':['alphas','betas','lower_bounds','upper_bounds','descriptors'],
               'gamma_uncertain':['alphas','betas','descriptors'],
               'gumbel_uncertain':['alphas','betas','descriptors'],
               'frechet_uncertain':['alphas','betas','descriptors'],
               'weibull_uncertain':['alphas','betas','descriptors'],
               'histogram_bin_uncertain':['num_pairs','abscissas','ordinates','counts','descriptors'],
               'poisson_uncertain':['lambdas','descriptors'],
               'binomial_uncertain':['prob_per_trial','num_trials','descriptors'],
               'negative_binomial_uncertain':['prob_per_trial','num_trials','descriptors'],
               'geometric_uncertain':['prob_per_trial','descriptors'],
               'hypergeometric_uncertain':['total_population','selected_population','num_drawn','descriptors'],
               'histogram_point_uncertain':['num_pairs','abscissas','counts','descriptors'],
               'interval_uncertain':['num_intervals','interval_probs','interval_bounds','descriptors'],
               'continuous_state':['initial_state','lower_bounds','upper_bounds','descriptors'],
               'discrete_state_range':['initial_state','lower_bounds','upper_bounds','descriptors'],
               'discrete_state_set_integer':['initial_state','num_set_values','set_values','descriptors'],
               'discrete_state_set_real':['initial_state','num_set_values','set_values','descriptors']
               }

property_types={'continuous_design':{
                                     'initial_state':float,
                                     'lower_bounds':float,
                                     'upper_bounds':float,
                                     'scale_types':str,
                                     'scales':float,
                                     'descriptors':str
                                     },
                'discrete_design_range':{
                                         'initial_point':int,
                                         'lower_bounds':int,
                                         'upper_bounds':int,
                                         'descriptors':str
                                         },
                'discrete_design_set_integer':{'initiareal_point':int,
                                               'num_set_values':int,
                                               'set_values':int,
                                               'descriptors':str
                                               },
                'discrete_design_set_real':{'initial_point':float,
                                            'num_set_values':int,
                                            'set_values':float,
                                            'descriptors':str
                                            },
                'normal_uncertain':{'means':float,
                                    'std_deviations':float,
                                    'lower_bounds':float,
                                    'upper_bounds':float,
                                    'descriptors':str
                                    },
                'lognormal_uncertain':{'means':float,
                                       'std_deviations':float,
                                       'error_factors':float,
                                       'lambdas':float,
                                       'zetas':float,
                                       'lower_bounds':float,
                                       'upper_bounds':float,
                                       'descriptors':float
                                       },
                'uniform_uncertain':{'lower_bounds':float,
                                     'upper_bounds':float,
                                     'descriptors':str
                                     },
                'loguniform_uncertain':{'lower_bounds':float,
                                        'upper_bounds':float,
                                        'descriptors':str
                                        },
                'triangular_uncertain':{'modes':float,
                                        'lower_bounds':float,
                                        'upper_bounds':float,
                                        'descriptors':str
                                        },
                'exponential_uncertain':{'betas':float,
                                         'descriptors':str
                                         },
                'beta_uncertain':{'alphas':float,
                                  'betas':float,
                                  'lower_bounds':float,
                                  'upper_bounds':float,
                                  'descriptors':str
                                  },
                'gamma_uncertain':{'alphas':float,
                                   'betas':float,
                                   'descriptors':str
                                   },
                'gumbel_uncertain':{'alphas':float,
                                   'betas':float,
                                   'descriptors':str
                                   },
                'frechet_uncertain':{'alphas':float,
                                   'betas':float,
                                   'descriptors':str
                                   },
                'weibull_uncertain':{'alphas':float,
                                   'betas':float,
                                   'descriptors':str
                                   },
                'histogram_bin_uncertain':{'num_pairs':int,
                                           'abscissas':float,
                                           'ordinates':float,
                                           'counts':float,
                                           'descriptors':str},
                'poisson_uncertain':{'lambdas':float,
                                     'descriptors':str
                                     },
                'binomial_uncertain':{'prob_per_trial':float,
                                      'num_trials':int,
                                      'descriptors':str
                                      },
                'negative_binomial_uncertain':{'prob_per_trial':float,
                                      'num_trials':int,
                                      'descriptors':str
                                      },
                'geometric_uncertain':{'prob_per_trial':float,
                                      'descriptors':str
                                      },
                'hypergeometric_uncertain':{'total_population':int,
                                            'selected_population':int,
                                            'num_drawn':int,
                                            'descriptors':str
                                            },
                'histogram_point_uncertain':{'num_pairs':int,
                                             'abscissas':float,
                                             'counts':float,
                                             'descriptors':str
                                             },
                'interval_uncertain':{'num_intervals':int,
                                      'interval_probs':float,
                                      'interval_bounds':float,
                                      'descriptors':str
                                      },
                'continuous_state':{'initial_state':float,
                                    'lower_bounds':float,
                                    'upper_bounds':float,
                                    'descriptors':str
                                    },
                'discrete_state_range':{'initial_state':float,
                                    'lower_bounds':float,
                                    'upper_bounds':float,
                                    'descriptors':str
                                    },
                'discrete_state_set_integer':{'initial_state':int,
                                              'num_set_values':int,
                                              'set_values':int,
                                              'descriptors':str
                                              },
                'discrete_state_set_real':{'initial_state':float,
                                           'num_set_values':float,
                                           'set_values':float,
                                           'descriptors':str
                                           },
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

  def hasProperty(self,propertyname):
    """check if the domain has a property with name 'propertyname'
    Override with subclass method"""
    return False

  def updateProperty(self,propertyname,value):
    """update a property of the domain
    Override with subclass method"""
    return False
    
class DomainCRSD(Domain):
  """Class for a Continuous Real Single Dimension domain
  
  The Domain is defined by the bounds of a segment in real space
  """ 

  def __init__(self):
    self._values=[]
    self.dakotatype='continuous_design'

  def get_bounds(self):
    return self._values

  def set_bounds(self,start,end):
    if isinstance(start,float) and isinstance(end,float) and start<end:
      self.values=[start,end]
    else:
      logger.error("Incorrect types and/or incorrect ordering of bounds")

  def getproperties(self,):
    return {'lower_bounds':self._values[0], 'upper_bounds':self._values[1]}

  def hasProperty(self,propertyname):
    """check if the domain has a property with name 'propertyname'
    Overrides parent method"""
    if propertyname in ('lower_bounds', 'upper_bounds'): return True
    return False

  def updateProperty(self,propertyname,value):
    """update a property of the domain
    Overrides parent method
    Returns True if successful, False otherwise"""
    if propertyname=='lower_bounds':
      self._values[0]=value
      return True
    elif propertyname=='upper_bounds':
      self._values[1]=value
      return True
    else:
      return False

class Variable(object):
  """Class for reading and writing Dakota variables"""

  def __init__(self,descriptor):
    self.descriptor=descriptor
    self._initial=None # stores the state of the variable
    self._domain=Domain() # boundaries for the allowed states of the variable

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

  def getState(self):
    return self._initial

  def getStateProperties(self):
    """Properties related to the state of the variable.
     Override with subclass method"""
  return {}

  def getproperties(self):
    """The properties of a variable are the union of its descriptor, the state
    of the variable, and the boundaries for the variable""" 
    return {'descriptors':self.descriptor}+self.getStateProperties()+self._domain.getproperties()

  def isPropertyOfDomain(self,propertyname):
    return self._domain.hasProperty(propertyname)

  def updateStateProperty(self,propertyname,value):
    """"Update a property of the variable
    Override with subclass method"""
    return False

  def updateProperty(self,propertyname,value):
    """Update either the descriptor, a domain property, or a state property"""
    if propertyname=='descriptor':
      self.descriptor=value
    elif self.isPropertyOfDomain(propertyname):
      self._domain.updateProperty(propertyname,value)
    else:
      self.updateStateProperty(propertyname,value)

class VariableCRSD(Variable):
  """Class for a Continuous Real Single Dimension variable.
  Only admits domains of class DomainCRSD"""

  def __init__(self,descriptor):
    self.descriptor=descriptor
    self._initial=None # stores the state of the variable
    self._domain=DomainCRSD() # boundaries for the allowed states of the variable

  def domainChecks(self,domain):
    """Domain type must be of certain type.
    Overrides parent method"""
    if type(domain).__name__=='DomainCRSD': return True
    return False

  def getStateProperties(self):
    """Properties related to the state of the variable.
    Overrides parent method"""
    return {'initial_state':self._initial}

  def updateStateProperty(self,propertyname,value):
    """"Update a property of the variable
    Overrides parent method
    Returns True if successful, False otherwise"""
    if propertyname=='initial_state':
      self._initial=value
      return True
    return False

# Instantiate object by dakota variable type
daktype2Var={'continuous_design':VariableCRSD,
             'discrete_design_range':Variable,
             'discrete_design_set_int':Variable,
             'discrete_design_set_real':Variable,
             'normal_uncertain':Variable,
             'lognormal_uncertain':Variable,
             'uniform_uncertain':Variable,
             'loguniform_uncertain':Variable,
             'triangular_uncertain':Variable,
             'exponential_uncertain':Variable,
             'beta_uncertain':Variable,
             'gamma_uncertain':Variable,
             'gumbel_uncertain':Variable,
             'frechet_uncertain':Variable,
             'weibull_uncertain':Variable,
             'histogram_bin_uncertain':Variable,
             'poisson_uncertain':Variable,
             'binomial_uncertain':Variable,
             'negative_binomial_uncertain':Variable,
             'geometric_uncertain':Variable,
             'hypergeometric_uncertain':Variable,
             'histogram_point_uncertain':Variable,
             'interval_uncertain':Variable,
             'continuous_state':Variable,
             'discrete_state_range':Variable,
             'discrete_state_set_int':Variable,
             'discrete_state_set_real':Variable
             }

def variableFactory(dakotatype):
  return daktype2Var(dakotatype)

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

  def readFromFile(self,fhandle):
    '''Read information to update the variables of a homogeneous set'''
    # read in the type of variable
    current_position=fhandle.tell()
    l=fhandle.readline()
    dakota_type,n=[item.strip() for item in l.split('=')]
    if dakota_type not in dakotatypes: # check we are reading a homogeneous set
      fhandle.seek(current_position)
      return False
    self.dakotatype=dakota_type
    n=int(n)
    for _ in range(n): self._variables.append(variableFactory(self.dakotatype)())
    current_position=fhandle.tell()
    l=fhandle.readline().strip()
    while l:
      items=l.split()
      propertyname=items[0]
      if propertyname in propertynames[self.dakotatype]:
        conversion=property_types[self.dakotatype][propertyname] # from string to int, real, or string again
        values=[conversion(x) for x in items[1:]]
        for i in range(n):
          variable=self._variables[i]
          value=values[i]
          variable.updateProperty(propertyname,value)
        current_position=fhandle.tell()
        l=fhandle.readline().strip()
      else: #finished reading
        fhandle.seek(current_position)
        break
    return True

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
    """Write the variables set for a Dakota file
    """
    s=''
    if self.identifier: s+="id_variables = '"+self.identifier+"'\n" # Dakota needs enclosing of strings
    for hset in self._homogeneous:
      s+=hset.writeToString()+'\n'
    return self

  def writeToFile(self,fhandle):
    fhandle.write(self.writeToString())

  def readFromFile(self,fhandle):
    """read the whole variables section, or read a set identifier only"""
    l=fhandle.readline()
    # find out what are we reading
    if 'variables' in l: # we are reading at the very beginning of the variables section
      current_position=fhandle.tell()
      l=fhandle.readline()
    if 'id_variables' in l: # we are reading a variable set
      self.identifier=l.split('=')[:].strip() # read in the identifier string
    else:
      self.identifier='' # empty identifier string
      fhandle.seek(current_position) # go back one line
    hset=VariableHomogeneousSet('init_type')
    while hset.readFromFile(fhandle):
      self.insertHomogeneousSet(hset)
    if not self._homogeneous: return False # unsuccessful reading
    return True

class SectionVariables(object):
  """Reads and write to the 'variables' section of the Dakota inputs file
  May contain one or more identifier sets"""

  def __init__(self):
    self._variableset=[]

  def readFromFile(self,fhandle):
    v=VariableSet(None)
    while v.readFromFile(fhandle):
      self._variableset.append(v)
      v=VariableSet(None)

  def writeToString(self):
    s='variables,\n'
    for hset in self._variableset:
      s+=hset.writeToString()+'\n'
    return s

  def writeToFile(self,fhandle):
    fhandle.write(self.writeToString())

