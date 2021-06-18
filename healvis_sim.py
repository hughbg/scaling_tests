#!/usr/bin/env python
# coding: utf-8

# In[59]:


import numpy as np
import argparse
from config import telescope_config
from timeit import timeit
from resource import getrusage, RUSAGE_SELF

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nant", default=10, type=int,
                                   help="Number of antennas")
    parser.add_argument("--nchan", default=10, type=int,
                                   help="Number of channels")
    parser.add_argument("--ntime", default=1, type=int,
                                    help="Number of times")
    parser.add_argument("--nsource", default=0, type=int,
                                    help="Number of sources")
    return parser

args = create_parser().parse_args()

obs, gsm = telescope_config("healvis", nant=args.nant, nfreq=args.nchan, ntime=args.ntime, nsource=args.nsource)

sim_time = timeit(stmt = "obs.make_visibilities(gsm, beam_pol='XX')", globals=globals(), number=1)

usage = getrusage(RUSAGE_SELF)
print("SIM", sim_time, usage.ru_maxrss/1000.0/1000)      # Usage in GB


