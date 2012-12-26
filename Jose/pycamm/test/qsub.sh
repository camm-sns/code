#!/bin/bash

PBS_JOBID=$(qsub -q premium minimize.pbs)
echo "qsub -q premium minimize.pbs"
sleep 1s
PBS_JOBID=$(qsub -q premium -W depend=afterok:${PBS_JOBID}@sdb annealing.pbs)
echo "qsub -q premium -W depend=afterok:${PBS_JOBID}@sdb annealing.pbs"
sleep 1s
for run in  01 02 03 04;do
  PBS_JOBID=$(qsub -q premium -W depend=afterok:${PBS_JOBID}@sdb production$run.pbs)
  echo "qsub -q premium -W depend=afterok:${PBS_JOBID}@sdb production$run.pbs"
  sleep 1s
fi

done
