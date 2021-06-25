#!/usr/bin/env python
# coding: utf-8

from timeit import timeit
from hera_sim.visibilities import VisCPU
from config import telescope_config
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
    parser.add_argument("--use_gpu", default=False, dest="use_gpu", action="store_true",
                                    help="Use the gpu simulator")
    parser.add_argument("--use_astropy", default=False, dest="use_astropy", action="store_true",
                                    help="Use az corrections")
    parser.add_argument("--use_az_fix", default=False, dest="use_az_fix", action="store_true",
                                    help="Use az fix corrections")
    parser.add_argument("--use_beam_pix", default=False, dest="use_beam_pix", action="store_true",
                                    help="Use pixel beams")


    return parser

BEAM_PIX = 20

args = create_parser().parse_args()

uvdata, beam, beam_dict, freqs, ra_dec, flux = \
    telescope_config("hera_sim", nant=args.nant, nfreq=args.nchan, ntime=args.ntime, nsource=args.nsource)

if args.use_az_fix or args.use_astropy:
    if args.use_gpu:
        raise RuntimError("Can't use GPU with az corrections")
    
    from vis_cpu.vis_cpu import VisCPU as VisCPU_hugh
    simulator = VisCPU_hugh(
        uvdata = uvdata,
        beams = beam,
        sky_freqs = freqs,
        point_source_pos = ra_dec,
        point_source_flux = flux,
        which = "astropy" if args.use_astropy else "az_fix"
    )

else:
    simulator = VisCPU(
        uvdata = uvdata,
        beams = beam,
        beam_ids = list(beam_dict.values()),
        sky_freqs = freqs,
        point_source_pos = ra_dec,
        point_source_flux = flux,
        bm_pix = BEAM_PIX,
        use_gpu = args.use_gpu,
        use_pixel_beams = args.use_beam_pix
    )

simulator.simulate()
sim_time = timeit(stmt = "simulator.simulate()", globals=globals(), number = 1)

usage = getrusage(RUSAGE_SELF)
print("SIM", sim_time, usage.ru_maxrss/1000.0/1000)      # Usage in GB
