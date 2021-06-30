import matplotlib.pyplot as plt
import os
import numpy as np
import yaml

PYUVSIM = False

def find_files(run_type, sim_titles):
    files = []
    for sim in sim_titles:
        fname = sim+"_"+run_type+".dat"
        if os.path.exists(fname):
            files.append(fname)
        else:
            print(fname, "missing")
    return files

def load_files_data(run_type, sim_titles):
    data = {}
    for f in find_files(run_type, sim_titles):
        simulator = f[:f.find(run_type)-1]
        data[simulator] = np.loadtxt(f)
    return data

def labels(run_type):
    if "_Time" in run_type:
        y_label = "Time (s)"
    else:
        y_label = "Memory (GB)"
    x_label = run_type.split("_")[0]
    return x_label, y_label

titles = []
with open("config.yaml") as yfile:
    config = yaml.load(yfile, Loader=yaml.FullLoader)

for sim in config.keys():
    if  isinstance(config[sim], dict) and "title" in config[sim]:
        titles += [ config[sim]["title"].replace(" ", "_") ]
    
for run_type in [ "Baselines_Script_Time", "Baselines_Memory_usage", "Baselines_Simulation_Time", 
                "Channels_Memory_usage", "Channels_Script_Time", "Channels_Simulation_Time",
                "Sources_Memory_usage", "Sources_Script_Time", "Sources_Simulation_Time",
                "Times_Memory_usage", "Times_Script_Time", "Times_Simulation_Time" ]:
    run_type_data = load_files_data(run_type, titles)
    _max = 0
    for sim in sorted(run_type_data.keys()):
        x = run_type_data[sim][:, 0]
        y = run_type_data[sim][:, 1]
        y = np.where(y<=0 , np.nan, y)
        _max = max(_max, np.max(y))
        plt.plot(x, y, label=sim)
        labs = labels(run_type)
        plt.xlabel(labs[0])
        plt.ylabel(labs[1])
            
    #plt.yscale("log")
    plt.ylim(ymin=0,ymax=_max*1.05)
    plt.title(run_type)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(run_type+".png")
    plt.clf()


