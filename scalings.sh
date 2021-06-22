#!/bin/bash
#$ -cwd
#$ -j y
#$ -pe smp 1
#$ -l h_rt=24:00:00
#$ -l h_vmem=232G
#$ -l highmem

echo Running hera_sim_cpu_az sources
date
/data/home/apw737/anaconda3_herasim/bin/python scalings.py hera_sim_cpu_az sources
date
