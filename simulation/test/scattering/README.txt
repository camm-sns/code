Create S(Q,E) from I(Q,t)

  Command:

# Running using --indexes (see below for running using --rebinQ)
python sassenatasks.py genSQE "fqt_inc.hd5 fqt_coh.hd5" simulated.nxs --wsname simulated --indexes "2 4 6 8" --LoadSassena "TimeUnit:1.0" --SassenaFFT "FFTonlyRealPart:1,DetailedBalance:1,Temp:290" --NormaliseToUnity "RangeLower:-0.1,RangeUpper:0.1"

  Inputs:

	"fqt_inc.hd5, fqt_coh.hd5" incoherent and coherent structure factors, sassena files containing ten
	 histograms for I(Q,t). Each histogram has a different Q-value,	with Q from 0.1 to 1.0 every 0.1Angstroms^(-1).
	 Of these, we only transform to S(Q,E) those histograms with Q-values 0.3, 0.5, 0.7, and 0.9,
	 corresponding to workspace indexes 2, 4, 6, and 8 (--indexes "2 4 6 8")

  Options:

	--indexes "2 4 6 8" we only transform to S(Q,E) histograms with Q-values 0.3, 0.5, 0.7, and 0.9,
	  corresponding to workspace indexes 2, 4, 6, and 8 (--indexes "2 4 6 8")
	--LoadSassena "TimeUnit:1.0" time units in I(Q,t) are 1.0 picoseconds 
	--SassenaFFT "FFTonlyRealPart:1,DetailedBalance:1,Temp:290" Simulations were at 290K and applied
	  the detailed balance correction. We do Fourier transform of only the real part of I(Q,t)
	  because it was computed with orientaional average in Q-space. That means I(Q,t) must be real
	  and any imaginary part in I(Q,t) derives from finite orientational statistics.
	--NormaliseToUnity "RangeLower:-0.1,RangeUpper:0.1" Normalize S(Q,E) to unity in the [-0.1,0.1]meV range
	
  Output:
	simulated.nxs S(Q,E) containing four histograms.

# Running using --rebinQ
python sassenatasks.py genSQE "fqt_inc.hd5 fqt_coh.hd5" simulated.nxs --wsname simulated --rebinQ "0.2 0.2 1.0" --LoadSassena "TimeUnit:1.0" --SassenaFFT "FFTonlyRealPart:1,DetailedBalance:1,Temp:290" --NormaliseToUnity "RangeLower:-0.1,RangeUpper:0.1"
 Inputs:

    "fqt_inc.hd5, fqt_coh.hd5" incoherent and coherent structure factors, sassena files containing ten
     histograms for I(Q,t). Each histogram has a different Q-value, with Q from 0.1 to 1.0 every 0.01Angstroms^(-1).
     We rebin in Q space to end up with four values, namely 0.3, 0.5, 0.7, and 0.9.

  Options:

    --rebinQ "0.2 0.2 1.0" rebin from 0.2 to 1.0 every 0.2A^{-1}. Thus, we end up with Q-values
      0.3, 0.5, 0.7, and 0.9.
    --LoadSassena "TimeUnit:1.0" time units in I(Q,t) are 1.0 picoseconds 
    --SassenaFFT "FFTonlyRealPart:1,DetailedBalance:1,Temp:290" Simulations were at 290K and applied
      the detailed balance correction. We do Fourier transform of only the real part of I(Q,t)
      because it was computed with orientaional average in Q-space. That means I(Q,t) must be real
      and any imaginary part in I(Q,t) derives from finite orientational statistics.
    --NormaliseToUnity "RangeLower:-0.1,RangeUpper:0.1" Normalize S(Q,E) to unity in the [-0.1,0.1]meV range
    
  Output:
    simulated.nxs S(Q,E) containing four histograms.