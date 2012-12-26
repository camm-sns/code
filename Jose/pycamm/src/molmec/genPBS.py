
import os
import sys
import argparse

parser = argparse.ArgumentParser(description='script generating *.pbs submission files')
parser.add_argument('--wd',help='working directory, Ex: --wd=/tmp/username')
parser.add_argument('--queue',help='name of the qsub queue. Ex: --queue=premium')
args = parser.parse_args()
#reqargs=[]
#if args.kargs: reqargs=args.kargs.split(',')
#optargs={}
#if args.kwargs: optargs=dict( map( lambda x: x.split('='), args.kwargs.split(',') ) )

# Options for submission of minimization run(s)
opts_min={'_WALLTIME_':'0:30:00',
          '_NCORE_':48, # total number of required cores
          '_CONFILE_':'minimization.conf',
          '_OUTFILE_':'minimization.out',
          }

# Options for submission of annealing run(s)
opts_ann={'_WALLTIME_':'0:59:00',
          '_NCORE_':48, # total number of required cores
          '_CONFILE_':'annealing.conf',
          '_OUTFILE_':'annealing.out',
          }

#Options for submission of production run(s)
opts_pro={'_WALLTIME_':'0:59:00',
          '_NCORE_':48,    # total number of required cores
          '_NRUN_':4,      # number of consecutive production qsub submissions
          '_CONFILE_':'productionXX.conf',
          '_OUTFILE_':'productionXX.out',
          }


#template submission script
#Do not edit this template, but change opts dictionary
template="""#PBS -S /bin/bash
#PBS -j oe
#PBS -V
#PBS -l walltime=_WALLTIME_,mppwidth=_NCORE_

#submit simulations
cd _WORKDIR_
aprun -n _NCORE_ namd2 _CONFILE_ > _OUTFILE_ # & only one job, no need to send it to the background
#wait  #required when submitting jobs with '&'

"""

def genPBS(opts, file_name, srun=None):
  tpl=template
  for (key,val) in opts.items(): tpl=tpl.replace(key,str(val))
  tpl=tpl.replace('_WORKDIR_',args.wd)
  if srun:
    tpl=tpl.replace('productionXX', 'production%s'%srun)
  open(file_name,'w').write(tpl)

genPBS(opts_min, 'minimization.pbs')  # create the PBS minimization job
genPBS(opts_ann, 'annealing.pbs') # create the PBS annealing job

# create the PBS run jobs and productionXX.conf files
# initialize runlist for later
def genConf(proprev,pronext,srun):
  tpl=open('production.conf').read()
  tpl=tpl.replace('_PROPREV_',proprev)
  tpl=tpl.replace('_PRONEXT_',pronext)
  open('production%s.conf'%srun,'w').write(tpl)

proprev='annealing'
runlist=''
for irun in range(1,1+opts_pro['_NRUN_']):
  srun='%02d'%irun
  runlist += ' '+srun
  genPBS(opts_pro, 'production%s.pbs'%srun, srun=srun)
  pronext='production%s'%srun
  genConf(proprev, pronext, srun)
  proprev=pronext

#template to create Bash script to submit the PBS jobs
template="""#!/bin/bash

PBS_JOBID=$(qsub -q _QUEUE_ minimize.pbs)
echo \"qsub -q _QUEUE_ minimize.pbs"
sleep 1s
PBS_JOBID=$(qsub -q _QUEUE_ -W depend=afterok:${PBS_JOBID}@sdb annealing.pbs)
echo \"qsub -q _QUEUE_ -W depend=afterok:${PBS_JOBID}@sdb annealing.pbs"
sleep 1s
for run in _RUNLIST_;do
  PBS_JOBID=$(qsub -q _QUEUE_ -W depend=afterok:${PBS_JOBID}@sdb production$run.pbs)
  echo \"qsub -q _QUEUE_ -W depend=afterok:${PBS_JOBID}@sdb production$run.pbs\"
  sleep 1s
fi

done
"""

tpl=template
tpl=tpl.replace('_RUNLIST_',runlist)
tpl=tpl.replace('_QUEUE_',args.queue)
open('qsub.sh','w').write(tpl)
os.system('chmod u+x qsub.sh')

sys.exit(0)
