#!/usr/bin/env python
# coding: utf-8

import numpy as np
from config import telescope_config
from pyuvsim import uvsim, simsetup
from pyuvsim.telescope import BeamList
from hera_sim.visibilities import VisCPU
try:
    from vis_cpu.vis_cpu import VisCPU as VisCPU_hugh
except: pass
from vis_cpu.conversions import equatorial_to_eci_coords
from astropy.coordinates import EarthLocation
from astropy.time import Time

# pyuvsim
uvdata, beam, beam_dict, sky_model = telescope_config("pyuvsim", 2, 1, 1, 1, False)

uvd_out = uvsim.run_uvdata_uvsim(uvdata, BeamList(beam), beam_dict=beam_dict, catalog=simsetup.SkyModelData(sky_model))

sim_auto = uvd_out.get_data(0, 0, "XX")[0][0]
sim_cross = uvd_out.get_data(0, 1, "XX")[0][0]

print("pyuvsim -------------")
print("auto amp:", np.abs(sim_auto))
print("cross amp:", np.abs(sim_cross), "phase:", np.angle(sim_cross))

print("V",uvd_out.data_array)
print("UVW", uvd_out.uvw_array)


# various versions of hera_sim

# ASTROPY

uvdata, beam, beam_dict, freqs, ra_dec, flux = telescope_config("hera_sim", 2, 1, 1, 1, False)
if False:
    simulator = VisCPU(
        uvdata = uvdata,
        beams = beam,
        beam_ids = list(beam_dict.values()),
        sky_freqs = freqs,
        point_source_pos = ra_dec,
        point_source_flux = flux,
        use_pixel_beams=False,
        az_za_corrections = [ "astropy", "uvbeam_az" ],
        precision = 1
    )


    simulator.simulate()

    sim_auto = simulator.uvdata.get_data(0, 0, "XX")[0][0]
    sim_cross = simulator.uvdata.get_data(0, 1, "XX")[0][0]

    print("hera_sim old astropy ----")
    print("auto amp:", np.abs(sim_auto))
    print("cross amp:", np.abs(sim_cross), "phase:", np.angle(sim_cross))
    print("V", simulator.uvdata.data_array)
#except:
#    print("old astropy didn't run")
#exit()

# simulate_vis
"""
uvdata, beam, beam_dict, freqs, ra_dec, flux = telescope_config("hera_sim", 2, 1, 1, 1, True)

simulator = VisCPU_hugh(
    uvdata = uvdata,
    beams = beam,
    sky_freqs = freqs,
    point_source_pos = ra_dec,
    point_source_flux = flux,
    which = "az_fix"
)

simulator.simulate()

sim_auto = simulator.uvdata.get_data(0, 0, "XX")[0][0]
sim_cross = simulator.uvdata.get_data(0, 1, "XX")[0][0]

print("hera_sim astropy ----")
print("auto amp:", np.abs(sim_auto))
print("cross amp:", np.abs(sim_cross), "phase:", np.angle(sim_cross))
print("V", simulator.uvdata.data_array)
"""

# AZ_FIX
uvdata, beam, beam_dict, freqs, ra_dec, flux = telescope_config("hera_sim", 2, 1, 1, 1, False)

location = EarthLocation.from_geodetic(lat=-30.7215, lon=21.4283,  height=1073.)
obstime = Time(uvdata.time_array[0], format='jd', scale='utc')

ra, dec = equatorial_to_eci_coords(ra_dec[:, 0], ra_dec[:, 1], obstime, location)
ra_dec[:, 0] = ra
ra_dec[:, 1] = dec

simulator = VisCPU (
    uvdata = uvdata,
    beams = beam,
    beam_ids = list(beam_dict.values()),
    sky_freqs = freqs,
    point_source_pos = ra_dec,
    point_source_flux = flux,
    use_pixel_beams = False,
    polarized = True
)

simulator.simulate()

sim_auto = simulator.uvdata.get_data(0, 0, "XX")[0][0]
sim_cross = simulator.uvdata.get_data(0, 1, "XX")[0][0]

print("hera_sim az_fix ----")
print("auto amp:", np.abs(sim_auto))
print("cross amp:", np.abs(sim_cross), "phase:", np.angle(sim_cross))
print("V",simulator.uvdata.data_array)
print("UVW", simulator.uvdata.uvw_array)
