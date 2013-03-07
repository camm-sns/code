'''
Created on Jan 4, 2013

Queue object
'''
import logging
logger = logging.getLogger('simhost.queue')

class Queue(object):
  """ Object containing information for a job queue"""

  def __init__(self):
    self.name=None
    self.server=None
    self.of_interest=('queue_type', 'resources_max.walltime', 'Priority','max_user_run')

  def getinfo(self,mode):
    """ collect queue info """
    out=''; err=''
    if mode=='ssh':
      pass # not implemented
    elif mode=='local':
      import subprocess
      proc=subprocess.Popen(['qstat','-Qf', self.name+'@'+self.server.name],stdout=subprocess.PIPE)
      out,err=proc.communicate()
    else:
      out=mode
    if err:
      logger.error('qstat returned error:', err)
    for line in out.split('\n')[1:]:
      attr,val=[x.strip() for x in line.split('=')]
      self.__setattr__(attr,val)

  def __setattr__(self,attr,val):
    if attr in self.of_interest:
      self.__dict__[attr]=val

  def toElementTreeElement(self):
    """save as xml.ElementTree.Element object"""
    from xml.etree.ElementTree import Element
    el=Element(self.__class__.__name__)
    for attribute in self.of_interest:
        value=self.__getattribute__(attribute)
        if value: el.attrib[attribute[1:]]=str(value)
    return el

  def fromElementTreeElement(self, el):
    """ read from xml.ElementTree.Element object.
    Overloaded __setattr__ takes care of assigning the correct types
    """
    for key,value in el.attrib.items():
      self.__setattr__(key, value)
    return self
