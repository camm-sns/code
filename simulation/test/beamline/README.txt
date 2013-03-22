Run the script:
  Inputs:
	- simulated S(Q,E), simulated.nxs
	- resolution file, resolution.nxs
  	- beamline model, model.txt
	- expdata (optional) experimental data. If passed, output convolved will be binned as expdata.
	- costfile (optional). If passed, the cost of comparing convolved and expdata will be saved to this file.
  Output:
	- convolved S(Q,E), convolved.nxs

python convolve.py  lowTresolution --model model.txt --simulated simulated.nxs --resolution resolution.nxs --convolved convolved.nxs --expdata LiCl_290K_m50_50.nxs --costfile cost.txt --Fit="StartX:-50.0,EndX:50.0"

Compare your convolved.nxs with file convolved.bak.nxs
