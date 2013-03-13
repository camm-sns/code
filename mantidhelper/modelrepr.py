'''
Created on Mar 11, 2013

@author: jmborr
'''

""" Examples of function representations in string format

(composite=Convolution;name=TabulatedFunction,FileName="",Workspace=resolution,Scaling=1.0;
name=TabulatedFunction,FileName="",Workspace=ws_simulation,Scaling=1.0);name=TabulatedFunction,FileName="",Workspace=ws_elasltic,Scaling=1.0;name=FlatBackground,A0=0.001

(composite=Convolution;name=TabulatedFunction,FileName="",Workspace=resolution,Scaling=1.0;
(name=TabulatedFunction,FileName="",Workspace=ws_simulation;name=FlatBackground,A0=0.001))

(name=DiffSphere,NumDeriv=true,Q=0.69999999999999996,Intensity=1,Radius=1,Diffusion=1)

name=Gaussian,Height=26795,PeakCentre=3569,Sigma=315;name=LinearBackground,A0=-962,A1=0.3985

name=BackToBackExponential,I=275.41,A=0.0138215,B=0.00158227,X0=1356.34,S=106.762;
name=BackToBackExponential,I=546.746,A=0.00589434,B=0.0129046,X0=2950.66,S=67.7384;
name=LinearBackground,A0=2.41528,A1=0.0309741

name=LinearBackground,A0=0,A1=0;(composite=Convolution;
name=BivariateNormal,CalcVariances=false,Background=0,Intensity=0,Mcol=0,Mrow=0;
name=BackToBackExponential,I=0,A=1,B=0.05,X0=0,S=1)

name=LinearBackground,A0=0,A1=0;
(name=BivariateNormal,CalcVariances=false,Background=0,Intensity=0,Mcol=0,Mrow=0;
name=BackToBackExponential,I=0,A=1,B=0.05,X0=0,S=1)
"""
class FitFuncRepr(object):
  """ Loads a Mantid string representation of a fitting model into a
  (recursive) python object"""

  def addfunc(self,str_repr,index):
    """Insert function"""
    
    if ';' in str_repr[index:]:
      pass

  def readSingleFunc(self,str_repr,start):
    """Read non-composite function"""
    s=str_repr[start:]
    s.index(';')
    s=str_repr[start:s.find[';']]
    for (key,val) in [x.split('=') for x in s.split(',')]:
      if key=='name':
        self.name=val
      else:
        self._params.append((key,val))

  def __init__(self,str_repr):
    self.name=''
    self._params=[]
    self._members=[]
    self._parent=None
    if ';' in str_repr: # composite function
      pass
    else: # simple function
      self.loadSingleFunc(str_repr,0)

class Model(object):
  """Loads a string representation of a fitting model into a recursive python object
  
  Attributes:
    name: model name
    funcrepr: FitFuncRepr object representing the associated Mantid fitting function
  """

  def __init__(self,name,str_repr=None):
    """Initializes the model"""
    self.name=name
    self.funcrepr=FitFuncRepr(str_repr)
