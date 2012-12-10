'''
Record of file names required to run a molecular mechanics simulation
Created on Dec 7, 2012

@author: jmborr
'''

import os.path


class CosmosType(object):
  """Records may have one or more types, e.g., coordinates, topologies,
  force fields. Composite records will have more than one type, thus it
  is a 'has-a' relationship. A single record may have more than one type
  if the file contains, for instance, coordinates and velocities.
  
  """
  
  def __init__(self, ctype):
    self.__name = ctype


class CosmosEntryType(object):
  """Records may have one or more types, e.g., coordinates, topologies,
  force fields. Composite records will have more than one type, thus it
  is a 'has-a' relationship. A single record may have more than one type
  if the file contains, for instance, coordinates and velocities.
  
  """
  
  def __init__(self, ctype):
    self.__name = ctype


class CosmosEntry(object):
  """Record of the files required to run a molecular mechanics simulation.
  Typically one entry per file. If more than one file is required, then
  link the entry to the next entry. The whole link list acts as a single
  entry.
  
  """

  def __init__(self, *file_names, ctype):
    """Instantiate one or more CosmosEntry objects as a linked chain.  """
    self._basename = os.path.basename(file_names[0])
    self._dirname = os.path.dirname(file_names[0])
    self._ctype = ctype  # CosmosEntryType

  def GetNames(self,abspath=True):
    """ Return list of names for all entries.  """
    name = self._basename
    if abspath: name = os.path.join(self._dirname, self._basename)
    if self.IsComposite():
      return [name,] + self._next_entry.GetName(abspath) 
    return name

  def GetType(self):
    return self._type


class CosmosEntryLink(object):

  def __init__(self, ce, chain):
    self._next = None
    self._chain = chain
    if chain:
      chain[-1]._next = self 
      self.chain.append(ce)

  def __getattr__( self, method_name ):
    """ Pass request to next entry if not found( chain of responsibility ) """
    return getattr( self._next, method_name )


class CosmosList(object):
  
  def __init__(self, ctype):
    self._list = []
    self._ctype = ctype  # CosmosType object

  def append(self,centry):
    CosmosEntryLink(centry, self._clist)

  def __getattr__( self, method_name ):
    """ Pass request to first entry """
    return getattr( self._list[0], method_name )

