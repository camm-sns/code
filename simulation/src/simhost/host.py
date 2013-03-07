'''
Created on Jan 4, 2013

'''
import logging
logger = logging.getLogger('simhost.host')

class Host(object):
  """ Computer to run the simulations """

  def __init__(self):
    self.address='localhost'
    self.servers=[] # queue servers

  def collect_queues(self,mode):
    """ collect information on the host with qstat """
    import re
    from server import Server

    if isinstance(mode, str)==True:
      if 'server: ' in mode:
        pass
    elif mode=='ssh':
      pass
    elif mode=='local':
      import subprocess
      proc=subprocess.Popen(['qstat','-q'],stdout=subprocess.PIPE)
      out,err=proc.communicate()

    if err:
      logger.error('qstat returned error:', err)

    for name in re.findall('server\:\s+(\w+)\s+',out):
      sv = Server()
      sv.name=name
      sv.host=self
      sv.collect_queues(out)
      self.servers.append(sv)

