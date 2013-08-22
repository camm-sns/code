rm params* results* assembly* fit* Q*psf *log dakota.rst nohup.out
pkill dakota
pkill opt_driver
pkill python
CAMM=/usr/local/camm
cp $CAMM/dakota/opt* .
nohup dakota $1 &
