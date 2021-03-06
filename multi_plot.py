import matplotlib.pyplot as plt
import os
import numpy as np
import yaml

PYUVSIM = True

with open("config.yaml") as yfile:
    config = yaml.load(yfile, Loader=yaml.FullLoader)

def find_files(run_type, sim_titles):
    files = []
    for sim in sim_titles:
        fname = sim+"_"+run_type+".dat"
        if os.path.exists(fname):
            if PYUVSIM or "pyuvsim" not in fname: files.append(fname)
        else:
            print(fname, "missing")

    return files

def load_files_data(run_type, sim_titles):
    data = {}
    for f in find_files(run_type, sim_titles):
        simulator = f[:f.find(run_type)-1]
        data[simulator] = np.loadtxt(f)
        if len(data[simulator].shape) == 2 and data[simulator].shape[1] == 2:
            ok = "Shape ok"
        else:
            ok = "Shape is wrong"
        num_zeros = len(data[simulator][data[simulator] == 0])
        print(f+":", num_zeros, "zeros", len(data[simulator])-num_zeros, "values.", ok)
    return data

def labels(run_type):
    if "_Time" in run_type:
        y_label = "Time (s)"
    else:
        y_label = "Memory (GB)"
    x_label = run_type.split("_")[0]
    return x_label, y_label

titles = []


for sim in config.keys():
    if sim in config["run_these"]:
        titles += [ config[sim]["title"].replace(" ", "_") ]
    
colors = [ '#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080', '#ffffff', '#000000' ]

for run_type in [ "Baselines_Script_Time", "Baselines_Memory_usage", "Baselines_Simulation_Time", 
                "Channels_Memory_usage", "Channels_Script_Time", "Channels_Simulation_Time",
                "Sources_Memory_usage", "Sources_Script_Time", "Sources_Simulation_Time",
                "Times_Memory_usage", "Times_Script_Time", "Times_Simulation_Time" ]:
    run_type_data = load_files_data(run_type, titles)

    _max = 0
    color_index = 0
    for sim in sorted(run_type_data.keys()):
        x = run_type_data[sim][:, 0]
        y = run_type_data[sim][:, 1]
        x = x[y>0]
        y = y[y>0]
        _max = max(_max, np.max(y))
        y = np.where(y<=0 , np.nan, y)
        if len(x) == 1:
            plt.scatter(x, y, label=sim, s=8, color=colors[color_index])
        else: 
            plt.plot(x, y, label=sim, linewidth=0.6, color=colors[color_index])
        labs = labels(run_type)
        plt.xlabel(labs[0])
        plt.ylabel(labs[1])
        
        color_index += 1
        if color_index >= len(colors):
            raise RuntimeError("Not enough colors")
            
    #plt.yscale("log")
    plt.ylim(ymin=0,ymax=_max*1.1)
    plt.title(run_type)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(run_type+".png")
    plt.clf()


