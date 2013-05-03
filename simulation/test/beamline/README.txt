Command line:

python code/simulation/src/beamline/interpX.py itp_simple --assembled expdata.nxs --model model.txt --interpolated expdata_shifted.nxs

Input:

itp_simple: method employed for shift and subsequent interpolation
expdata.nxs: S(Q,E) for LiCl experimental system, T=290K
model.txt: file name for the model beamline string. Should contain "eshift=X", with X being the current value of the shift

Output:

expdata_shifted: output nexus file containing the shifted and interpolated S(Q,E)

====================================================================================
Command line:

python code/simulation/src/beamline/convolve.py convolution --resolution=resolution.nxs --simulated=simulated.nxs --expdata=expdata.nxs --convolved=convolved.nxs

Input:

resolution.nxs: LiCl experimental system, mirror of experimental signal at T=6K
expdata.nxs: LiCl experimental system, T=290K
simulated.nxs: LiCl simulated system, Q=42, T=290

Output:

convolved.nxs

====================================================================================                      
Command line:

python code/simulation/src/beamline/assemblemodel.py modelBEC --model model.txt --resolution resolution.nxs --convolved convolved.nxs --qvalues qvalues.dat --assembled assembled.nxs

Input:

model.txt: beamline model file is a single line, e.g, b0=1.3211; b1=0.00 e0=0.99; e1=1.9; c0=2.3
resolution.nxs: Nexus file containing the resolution. This will be used to produce a elastic line.
convolved.nxs: Nexus file containing the convolution of the simulated S(Q,E) with the resolution.
qvalues.dat: single-column file containing list of Q-values

Output:

assembled.nxs: output Nexus file containing the assembled S(Q,E) of the beamline model and the simulated S(Q,E)

====================================================================================    
                  
Command line:

python code/simulation/src/beamline/assemblemodel.py modelB_freeE_C --model modelB_freeE_C.txt --resolution resolution.nxs --convolved convolved.nxs --qvalues qvalues.dat --expdata LiCl_290K.nxs --costfile=costfile.dat --assembled=assembled.nxs --valsdata=valsdata.dat --derivdata=derivdata.dat --doshift=itp_simple

Input:

model.txt: beamline model file is a single line, e.g, b0=1.3211; b1=0.00 e0=0.99; e1=1.9; c0=2.3
resolution.nxs: Nexus file containing the resolution. This will be used to produce a elastic line.
convolved.nxs: Nexus file containing the convolution of the simulated S(Q,E) with the resolution.
qvalues.dat: single-column file containing list of Q-values
doshift: method to do the shift. Must be the name of a function in module interpX.py. Do not pass
	 this option if you don't want to the the shift along the E-axis

Output:

assembled.nxs: output Nexus file containing the assembled S(Q,E) of the beamline model and the simulated S(Q,E)
costfile.dat: output ASCII file containing the residuals
valsdata.dat: output ASCII file containing the values of the model function
derivdata.dat: output ASCII file containing the values of the partial derivatives of the model function
	       with respect to the fit parameters, except eshift.

====================================================================================                      
Command line:

python /code/simulation/src/beamline/resolution.py elasticLineLowTemp --insqe elasticLine.nxs --outres resolution.nxs

Input:

elasticLine.nxs: a Nexus file containing S(Q,E) at low temperature. One spectrum per Q-value.

Output:

resolution.nxs: output Nexus file containing Res(Q,E). Each spectrum is separately applied the Mantid::NormaliseToUnity algorithm.


