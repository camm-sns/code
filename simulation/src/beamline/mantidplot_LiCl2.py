import os
import sys
import shutil 


sys.path.append(os.environ['MANTIDPATH'])
from mantid.simpleapi import *
import MantidFramework
MantidFramework.mtd.initialise()
try:
  from mantidplot import *
except ImportError:
  pass

LiCl=Load(Filename="/SNS/users/vel/camm-sns/code/simulation/test/beamline/LiCl_260K.nxs")
for wi in xrange(mtd["LiCl"].getNumberHistograms()):	
        graph_spec = plotSpectrum ("Simulation_0.417", wi)
        l = graph_spec.activeLayer()
	l.setAxisScale(Layer.Left,1e-6,0.1,Layer.Log10)
	l.insertCurve("Simulation_0.443",wi)
	l.setAxisScale(Layer.Left,1e-6,0.1,Layer.Log10)
	l.insertCurve("LiCl", wi, True, 1)
	l.setAxisScale(Layer.Left,1e-6,0.1,Layer.Log10)
	s = PlotSymbol()
	s.setSize(QtCore.QSize(2, 2)) # or s.setSize(7)
	s.setBrush(QtGui.QBrush(Qt.darkYellow))
	s.setPen(QtGui.QPen(Qt.blue, 3))
	s.setStyle(PlotSymbol.Diamond)
	l.setCurveSymbol(2, s)
	l.replot() # redraw the plot layer object
	l.setCurveLineWidth(0,2.0)
	l.setCurveLineWidth(1,2.0)
	#l.setCurveLineColor(0,3)
        l.setCurveAxes(1,1,1)
	
	if wi == 0:
		l.setTitle("Q=0.5")
	elif wi == 1:
		l.setTitle("Q=0.7")
	elif wi == 2:
		l.setTitle("Q=0.9")
       

	l.setCanvasFrame(2, QtGui.QColor("black"))