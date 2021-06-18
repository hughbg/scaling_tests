#!/bin/bash
#$ -cwd
#$ -o scalings
#$ -j y
#$ -pe smp 1
#$ -l h_rt=2:00:00
#$ -l h_vmem=232G
#$ -l gpu=1
#$ -l owned

echo Running hera_sim_gpu antennas
date
/data/home/apw737/anaconda3_herasim/bin/python scalings.py hera_sim_gpu antennas
date
