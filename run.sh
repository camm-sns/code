rm params* results* assembly* fit* Q*psf *log output.csv dakota.rst nohup.out
CAMM=/tmp/code
cp $CAMM/dakota/dakota.in .
cp $CAMM/dakota/opt* .
nohup dakota dakota.in &
/usr/local/kepler/kepler.sh -runwf -nogui $CAMM/kepler/Strategist_1job.xml -LocalWorkingDirectory $PWD -LocalUserName $USER -RemoteLogin $USER@chadwick.sns.gov -CammDirectory $CAMM/simulation/src -NAMDBatchScript $CAMM/simulation/namd_camm-shorttest.pbs -SASSENABatchScript $CAMM/simulation/sassina_camm-shorttest.pbs -RemoteWorkingDirectory /data/.kepler-hpcc -RemoteBatchPath /usr/local/bin
