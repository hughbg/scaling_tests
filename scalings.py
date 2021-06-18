from matplotlib import use; use("Agg")
import matplotlib.pyplot as plt
import time
import subprocess
import numpy as np
import copy
import os, sys
import yaml

# Shorten the number of parameters for testing
def short(config):
    for param in [ "antennas", "channels", "times", "sources" ]:
        config[param[:-1]+"_numbers"] = config[param[:-1]+"_numbers"][:2] 
    return config

def get_time(pinterp, script, nant, nchan, ntime, nsource, option):
    command = [pinterp, script, '--nant', str(nant), '--nchan', str(nchan), '--ntime', str(ntime), '--nsource', str(nsource) ]

    if option is not None:
        command += [ "--"+option ]
    
    print(" ".join(command))
    sys.stdout.flush()
    script_time = sim_time = mem_used = 0.0
    for i in range(config["repetitions"]):
        start = time.time()
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr  = p.communicate()
        stdout = str(stdout, "utf-8")
        end = time.time()
        if p.returncode == 0:
            for line in str(stdout).split("\n"):
                if line[:3] == "SIM": 
                    l = line.split()
                    script_time += float(end-start)
                    sim_time += float(l[1])
                    mem_used += float(l[2]) 
                    print("Time", float(end-start), "Mem", float(l[2]))
        else: 
           print("Failed")
           print(stderr)
           script_time = sim_time = mem_used = np.nan
        time.sleep(1)

    return script_time/config["repetitions"], sim_time/config["repetitions"], mem_used/config["repetitions"]

def baseline(nant):
    num = 0
    for i in range(nant):
        for j in range(i+1, nant): num += 1
    return num

def plot(title, xlab, ylab, ylab_units, x, y, constants):
    plt.clf()
    long_title = title+". "+ylab+" vs. Num "+xlab+"\nConstants:"
    for p in constants.keys():
        long_title += " "+p+": "+str(constants[p])
    plt.title(long_title)
    plt.plot(x, y)
    plt.xlabel(xlab)
    plt.ylabel(ylab+" "+ylab_units)
    try:    # y might be all NaN
        plt.ylim(ymin=0,ymax=max(y)*1.05)
    except:
        pass
    fname = title.replace(" ", "_")+"_"+xlab.replace(" ", "_")+"_"+ylab.replace(" ", "_")
    plt.savefig(fname+".png")
    np.savetxt(fname+".dat", np.column_stack((x, y)))
 
def run(config, which_param):
    print("Run", config["title"])
    if not os.path.exists(config["pinterp"]):
        raise RuntimeError("Can't find Python interpreter "+config["pinterp"])
    if not os.path.exists(config["script"]):
        raise RuntimeError("Can't find script "+config["script"])

    print("Pre-run")		# Get the script loaded into cache by running a few times
    get_time(config["pinterp"], config["script"], config["defaults"]["antennas"],
	config["defaults"]["channels"], config["defaults"]["times"], config["defaults"]["sources"],
        config["option"])
    print("End pre-run")

    for param in [ which_param ]:
        script_time = np.zeros(len(config[param[:-1]+"_numbers"]))
        sim_time = np.zeros(len(config[param[:-1]+"_numbers"]))
        mem_used = np.zeros(len(config[param[:-1]+"_numbers"]))

        for i, num in enumerate(config[param[:-1]+"_numbers"]):
            script_time[i], sim_time[i], mem_used[i] = get_time(config["pinterp"], 
                                              config["script"], 
                                              num if param=="antennas" else config["defaults"][param], 
                                              num if param=="channels" else config["defaults"][param],
                                              num if param=="times" else config["defaults"][param],
                                              num if param=="sources" else config["defaults"][param],
                                              config["option"])

            xaxis_values = config[param[:-1]+"_numbers"]
            xlabel = param.capitalize()
            if param == "antennas": 
                xaxis_values = [ baseline(n) for n in config["antenna_numbers"] ]
                xlabel = "Baselines"
 
            constants = {}
            for p in [ "antennas", "channels", "times", "sources" ]:
                constants[p] = config["defaults"][p]
            del constants[param] 	# It is not being held constant
        
            plot(config["title"], xlabel, "Script Time", "(s)", xaxis_values, script_time, constants)
            plot(config["title"], xlabel, "Simulation Time", "(s)", xaxis_values, sim_time, constants)
            plot(config["title"], xlabel, "Memory usage", "(GB)", xaxis_values, mem_used, constants)




# The script used to do the simulation is specified with "script" in each
# config. The script must print a line of the form "SIM <simulation time (s)> <memory used (GB)>". 
# The script must take options --nant, --ntime, --nchan, --nsource

with open("config.yaml") as yfile:
    config = yaml.load(yfile, Loader=yaml.FullLoader)

# Promote some config values to the top level to indicate
# what we are running based on sys.argv[1]
config["title"] = config[sys.argv[1]]["title"]
config["script"] = config[sys.argv[1]]["script"]
if "option" in config[sys.argv[1]].keys():
    config["option"] = config[sys.argv[1]]["option"]
else:
    config["option"] = None

if sys.argv[1] == "healvis":
    config["defaults"] = { "antennas": 10, "channels" : 10, "times" : 10, "sources": 0 }
    config["source_numbers"] = [ 0 ]

if config["short_run"]: config = short(config)

run(config, sys.argv[2])
