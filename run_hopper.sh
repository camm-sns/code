rm params* results* assembly* fit* Q*psf *log output.csv dakota.rst nohup.out
CAMM=/tmp/code
cp $CAMM/dakota/dakota.in .
cp $CAMM/dakota/opt* .
nohup dakota dakota.in &
/usr/local/kepler/kepler.sh -runwf -nogui $CAMM/kepler/Strategist_1job.xml -LocalWorkingDirectory $PWD -LocalUserName $USER -RemoteLogin vlynch@hopper.nersc.gov -CammDirectory $CAMM/simulation/src -NAMDBatchScript $CAMM/simulation/namd_hopper_1job.pbs -SASSENABatchScript $CAMM/simulation/sassina_hopper_2jobs.pbs -RemoteWorkingDirectory /scratch/scratchdirs/vlynch -RemoteBatchPath /opt/torque/4.2.3.1/bin
