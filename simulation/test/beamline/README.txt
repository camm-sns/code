Command line:

python code/simulation/src/beamline/convolve.py convolution --resolution=resolution.nxs --simulated=simulated.nxs --expdata=expdata.nxs --convolved=convolved.nxs

Input:

resolution.nxs: LiCl experimental system, mirror of experimental signal at T=6K
expdata.nxs: LiCl experimental system, T=290K
simulated.nxs: LiCl simulated system, Q=42, T=290

Output:

convolved.nxs

===================================
                      
Command line:

python code/simulation/src/beamline/assemblemodel.py modelBEC --model model.txt --resolution resolution.nxs --convolved convolved.nxs --qvalues qvalues.dat --assembled assembled.nxs

Input:

model.txt: beamline model file is a single line, e.g, b0=1.3211; b1=0.00 e0=0.99; e1=1.9; c0=2.3
resolutio.nxsn: Nexus file containing the resolution. This will be used to produce a elastic line.
convolved.nxs: Nexus file containing the convolution of the simulated S(Q,E) with the resolution.
qvalues.dat: single-column file containing list of Q-values

Output:

assembled.nxs: output Nexus file containing the assembled S(Q,E) of the beamline model and the simulated S(Q,E)

===================================
                      
Command line:

python /code/simulation/src/beamline/resolution.py elasticLineLowTemp --insqe elasticLine.nxs --outres resolution.nxs

Input:

elasticLine.nxs: a Nexus file containing S(Q,E) at low temperature. One spectrum per Q-value.

Output:

resolution.nxs: output Nexus file containing Res(Q,E). Each spectrum is separately applied the Mantid::NormaliseToUnity algorithm.


