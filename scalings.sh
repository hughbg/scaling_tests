#!/bin/sh
#SBATCH --job-name='scaling_gpu'
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=232GB
#SBATCH --output=scaling-%j.log
#SBATCH --time=02:00:00
#SBATCH --partition=GPU


echo "Running hera_sim_gpu sources"
date
/users/hgarsden/scalings/anaconda3_herasim/bin/python scalings.py hera_sim_gpu sources
date

