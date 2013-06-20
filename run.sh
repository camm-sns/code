nohup dakota dakota.in &
CAMM=/tmp/code
/usr/local/kepler/kepler.sh -runwf -nogui $CAMM/kepler/Strategist.xml -LocalWorkingDirectory $PWD -LocalUserName $USER -RemoteLogin $USER@chadwick.sns.gov -CammDirectory $CAMM/simulation/src -NAMDBatchScript $CAMM/simulation/ubq_wb.pbs -SASSENABatchScript $CAMM/simulation/sassena.pbs
