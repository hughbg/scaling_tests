import os
from datetime import datetime
import yaml

with open("config.yaml") as yfile:
    config = yaml.load(yfile, Loader=yaml.FullLoader)


ON_ILIFU = os.path.isfile("/opt/slurm/bin/sbatch")


def gen_batch_header(use_gpu=False):
    
    time = config["gpu_run_time"] if use_gpu else config["run_time"]

    if ON_ILIFU:
        batch_header="""#!/bin/bash
#SBATCH --job-name='scaling'
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=232GB
#SBATCH --output=scaling-%j.log
#SBATCH --time="""+time

    else:
        batch_header="""#!/bin/bash
#$ -cwd
#$ -o scalings
#$ -j y
#$ -pe smp 1
#$ -l h_rt="""+time+"""
#$ -l h_vmem=232G"""
    
    if use_gpu:
        if ON_ILIFU:
            batch_header += "\n#SBATCH --partition=GPU"
        else:
            batch_header += "\n#$ -l gpu=1\n#$ -l owned"

    return batch_header

def run_scaling(which, param, use_gpu=False):
    f = open("scalings.sh", "w")
    f.write(gen_batch_header(use_gpu)+"\n\n")
    f.write("echo Running "+which+" "+param+"\n")
    f.write("date"+"\n")
    f.write(config["pinterp"]+" scalings.py "+str(which)+" "+str(param)+"\n")
    f.write("date"+"\n")
    f.close()
    
    if config["run_as_batch"]:
        if ON_ILIFU:
            os.system("sbatch scalings.sh")
        else:
            os.system("qsub scalings.sh")
    else:
        os.system("nice sh scalings.sh")

for p in [ "antennas", "channels", "times", "sources" ]:
    #run_scaling("hera_sim_cpu", p)
    #run_scaling("hera_sim_cpu_az", p)          # Not installed
    run_scaling("hera_sim_gpu", p, True)
    exit()
    #run_scaling("healvis", p)
    #run_scaling("pyuvsim", p)

