Command line:

python initparams.py modelB_freeE_C --model modelB_freeE_C.xml --resolution resolution.nxs  --qlist "0.3 0.5 0.7 0.9" --pdb LiCl_watBox30.pdb --expdata LiCl_290K_4Qs.nxs --initparfile modelB_freeE_C_init.txt

Input:

modelB_freeE_C.xml      beamline template model file (xml format)
resolution.nxs:         Nexus file containing the model resolution
"0.3 0.5 0.7 0.9"       list of Q-values
LiCl_watBox30.pdb       PDB file containing conformation of the system
LiCl_290K_4Qs.nxs       Nexus file containing the experimental data

Output:

modelB_freeE_C_init.txt Output the initial parameters as a string in file with name initparfile

====================================================================================
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

python code/simulation/src/beamline/assemblemodel.py modelB_freeE_C --model  modelB_freeE_C.txt --resolution=resolution.nxs --convolved=convolved.nxs --expdata=LiCl_290K.nxs --costfile=costfile.dat --assembled=assembled.nxs --derivdata=1 --derivexclude="b1" --doshift=itp_simple

Input:

model.txt: beamline model file is a single line, e.g, b0=1.3211; b1=0.00 e0=0.99; e1=1.9; c0=2.3
resolution.nxs: Nexus file containing the resolution. This will be used to produce a elastic line.
convolved.nxs: Nexus file containing the convolution of the simulated S(Q,E) with the resolution.
expdata: optional, experimental nexus file. If passed, output convolved will be binned as expdata.
derivdata: optional, set to 1 if to perform analytic derivatives (store in costfile if provided)
derivexclude: optional, string containing space-separated parameters for which partial derivatives will not be computed
doshift: method to do the shift. Must be the name of a function in module interpX.py. Do not pass
	 this option if you don't want to the the shift along the E-axis

Output:

assembled.nxs: output Nexus file containing the assembled S(Q,E) of the beamline model and the simulated S(Q,E)
costfile.dat: output ASCII file containing the residuals

====================================================================================                      
Command line:

python /code/simulation/src/beamline/resolution.py elasticLineLowTemp --insqe elasticLine.nxs --outres resolution.nxs

Input:

elasticLine.nxs: a Nexus file containing S(Q,E) at low temperature. One spectrum per Q-value.

Output:

resolution.nxs: output Nexus file containing Res(Q,E). Each spectrum is separately applied the Mantid::NormaliseToUnity algorithm.


