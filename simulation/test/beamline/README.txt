Command line:

python code/simulation/src/beamline/convolve.py convolution --resolution=resolution.nxs --simulated=simulated.nxs --expdata=expdata.nxs --convolved=convolved.nxs

Input:

resolution.nxs: LiCl experimental system, mirror of experimental signal at T=6K
expdata.nxs: LiCl experimental system, T=290K
simulated.nxs: LiCl simulated system, Q=42, T=290

Output:

convolved.nxs
