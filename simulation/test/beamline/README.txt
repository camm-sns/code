Run the script:
  Inputs:
	- simulated S(Q,E), simulated.nxs
	- resolution file, resolution.nxs
  	- beamline model, model.txt
  Output:
	- convolved S(Q,E), convolved.nxs

python convolve.py  lowTresolution --model model.txt --simulated simulated.nxs --resolution resolution.nxs --convolved convolved.nxs --Fit="StartX:-50.0,EndX:50.0"

Compare your convolved.nxs with file convolved.bak.nxs
