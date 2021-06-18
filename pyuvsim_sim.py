#!/usr/bin/env python
# coding: utf-8

from timeit import timeit
from config import telescope_config
from pyuvsim import uvsim, simsetup
from pyuvsim.telescope import BeamList
import argparse
from resource import getrusage, RUSAGE_SELF

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nant", default=10, type=int,
                                   help="Number of antennas")
    parser.add_argument("--nchan", default=10, type=int,
                                   help="Number of channels")
    parser.add_argument("--ntime", default=1, type=int,
                                    help="Number of times")
    parser.add_argument("--nsource", default=100, type=int,
                                    help="Number of sources")

    return parser

args = create_parser().parse_args()

uvdata, beam, beam_dict, sky_model = \
    telescope_config("pyuvsim", nant=args.nant, nfreq=args.nchan, ntime=args.ntime, nsource=args.nsource)

sim_time = timeit(stmt = "uvsim.run_uvdata_uvsim(uvdata, BeamList(beam), beam_dict=beam_dict, \
         catalog=simsetup.SkyModelData(sky_model))", globals=globals(), number = 1)

usage = getrusage(RUSAGE_SELF)
print("SIM", sim_time, usage.ru_maxrss/1000.0/1000)      # Usage in GB
