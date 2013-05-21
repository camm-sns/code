'''
'''

import logging

class SimpleLogger(logging):
  '''Single-handle logger, plus a constructor having typical options'''

  def SimpleLogger(self, name, level='ERROR', format='[%(levelname)s] %(message)s', handler = logging.StreamHandler()):
    self._logger=logging.getLogger(name)
    self._logger.setLevel(getattr(logging, level))
    self._handler = handler
    self._handler.setFormatter(logging.Formatter(format))
    self._logger.addHandler(self._handler)

  def replace_handler(self, handler,format='[%(levelname)s] %(message)s'):
    self._logger.removeHandler(self._handler)
    self._handler = handler
    self._handler.setFormatter(logging.Formatter(format))
    self._logger.addHandler(self._handler)

  def addHandler(self,handler):
    raise Exception("SimpleLogger class admits one handler only")