'''
Created on Dec 7, 2012

@author: jmborr
'''

from cosmosentry import CosmosEntry

class CosmosEntryNamd(CosmosEntry):
  """Implements the files required to run a NAMD simulation."""

  def __init__(self,*file_names):
    