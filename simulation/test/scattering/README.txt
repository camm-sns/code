Create S(Q,E) from I(Q,t)

  Command:

python sassenatasks.py genSQE fqt.hd5 simulated.nxs --wsname simulated --indexes="2 4 6 8" --LoadSassena "TimeUnit:0.1" --SassenaFFT "FFTonlyRealPart:1,DetailedBalance:1,Temp:290" --NormaliseToUnity "RangeLower:-50.0,RangeUpper:50.0"

  Inputs:

	fqt.hd5 a sassena file containing ten histograms for I(Q,t).
	Each histogram has a different Q-value, with Q from 0.1 to 1.0 every 0.1Angstroms^(-1).
	Of these, we only transform to S(Q,E) those histograms with Q-values 0.3, 0.5, 0.7, and 0.9,
	corresponding to workspace indexes 2, 4, 6, and 8 (--indexes="2 4 6 8")

  Options:

	--indexes="2 4 6 8" we only transform to S(Q,E) histograms with Q-values 0.3, 0.5, 0.7, and 0.9,
	  corresponding to workspace indexes 2, 4, 6, and 8 (--indexes="2 4 6 8")
	--LoadSassena "TimeUnit:0.1" time units in I(Q,t) are 0.1picoseconds 
	--SassenaFFT "FFTonlyRealPart:1,DetailedBalance:1,Temp:290" Simulations were at 290K and applied
	  the detailed balance correction. We do Fourier transform of only the real part of I(Q,t)
	  because it was computed with orientaional average in Q-space. That means I(Q,t) must be real
	  and any imaginary part in I(Q,t) derives from finite orientational statistics.
	--NormaliseToUnity "RangeLower:-50.0,RangeUpper:50.0" Normalize S(Q,E) to unity in the -50 to 50 range
	
  Output:
	simulated.nxs S(Q,E) containing four histograms.

