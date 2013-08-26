rm params* results* assembly* fit* Q*psf *log dakota.rst nohup.out
pkill dakota
pkill opt_driver
pkill python
cp $2/../../dakota/opt* .
nohup dakota -i $1 -o dakota.log >/dev/null 2>/dev/null </dev/null  &
echo $!
