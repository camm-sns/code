'''
Created on Jan 4, 2013

'''
import logging
logger = logging.getLogger('simhost.server')

class Server(object):
  """ Hosting a list of Queues """
  
  def __init__(self):
    self.host=None
    self.name=None
    self.queues=[]

  def collect_queues(self,mode):
    """ collect information on the queues """
    from queue import Queue
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
    for qline in out.split(self.name)[1].split('\n')[4:]:
      q=Queue()
      q.name=qline.split()[0]
      q.server=self
      self.queues.append(q)
