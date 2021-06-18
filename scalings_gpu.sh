#!/bin/bash
#SBATCH --job-name='gpu_scaling'
#SBATCH --ntasks=1
#SBATCH --mem=240GB
#SBATCH --output=gs-%j-stdout.log
#SBATCH --time=01:00:00
#SBATCH --partition=GPU

module load cuda
echo "Running hera_sim_gpu"
date
#anaconda3_herasim/bin/python scalings.py hera_sim_gpu $1
/users/hgarsden/scalings/anaconda3_herasim/bin/python hera_sim_sim.py --nant 10 --nchan 10 --ntime 10 --nsource 10 --use_gpu
date
