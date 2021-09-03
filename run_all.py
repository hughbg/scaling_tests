import os
from datetime import datetime
import yaml

with open("config.yaml") as yfile:
    config = yaml.load(yfile, Loader=yaml.FullLoader)


ON_ILIFU = os.path.isfile("/opt/slurm/bin/sbatch")

def gen_batch_header(use_gpu=False, nproc=1):
    
    if config["short_run"]["enable"]:
        time = config["short_run"]["gpu_run_time"] if use_gpu else config["short_run"]["run_time"]
        mem = config["short_run"]["mem"]
    else:
        time = config["gpu_run_time"] if use_gpu else config["run_time"]
        mem = config["mem"]

    cpu = nproc     # Need to fix this all up for apocrita
    if use_gpu and not ON_ILIFU:
       mem /= 8
       cpu = 8

    if ON_ILIFU:
        batch_header="""#!/bin/bash
#SBATCH --job-name='scaling'
#SBATCH --ntasks="""+str(nproc)+"""
#SBATCH --cpus-per-task=1
#SBATCH --mem="""+str(mem)+"""G"""+"""
#SBATCH --output=scaling-%j.log
#SBATCH --time="""+time

    else:
        batch_header="""#!/bin/bash
#$ -cwd
#$ -j y
#$ -pe smp """+str(cpu)+"""
#$ -l h_rt="""+time+"""
#$ -l h_vmem="""+str(mem)+"""G"""

        if not config["short_run"]["enable"]:
            batch_header += """#$ -l highmem\n"""
    
    if use_gpu:
        if ON_ILIFU:
            batch_header += "\n#SBATCH --partition=GPU"
        else:
            batch_header += "\n#$ -l gpu=1\n#$ -l owned"

    return batch_header

def run_scaling(which, param, use_gpu=False):
    if "nproc" in config[which]:
        nproc = config[which]["nproc"]
    else:
        nproc = 1

    f = open("scalings.sh", "w")
    f.write(gen_batch_header(use_gpu, nproc)+"\n\n")
    f.write("echo Batch group id: "+str(os.getpid())+"\n")
    f.write("echo Running "+which+" "+param+"\n")
    f.write("date"+"\n")
    f.write(config["pinterp"]+" scalings.py "+str(which)+" "+str(param)+"\n")
    f.write("date"+"\n")
    f.close()

    if config["run_as_batch"]:
        if ON_ILIFU:
            os.system("sbatch scalings.sh | tee -a group_"+str(os.getpid())+".txt")
        else:
            os.system("qsub scalings.sh  | tee -a group_"+str(os.getpid())+".txt")
    else:
        os.system("nice sh scalings.sh")

if os.path.exists("group_"+str(os.getpid())+".txt"):
    os.remove("group_"+str(os.getpid())+".txt")
for p in [ "antennas", "channels", "times", "sources" ]:
    for sim in config["run_these"]:
        run_scaling(sim, p)     # Problem hera_gpu need True arg
