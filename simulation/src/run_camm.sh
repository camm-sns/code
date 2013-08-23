rm params* results* assembly* fit* Q*psf *log dakota.rst nohup.out
pkill dakota
pkill opt_driver
pkill python
CAMM=/home/vel/camm-sns/code
cp $CAMM/dakota/opt* .
nohup dakota -i $1 -o dakota.log >/dev/null </dev/null  &
echo $!
