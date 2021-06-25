#!/usr/bin/env python
# coding: utf-8

import numpy as np
from config import telescope_config
from pyuvsim import uvsim, simsetup
from pyuvsim.telescope import BeamList
from hera_sim.visibilities import VisCPU
from vis_cpu.vis_cpu import VisCPU as VisCPU_hugh


# pyuvsim
uvdata, beam, beam_dict, sky_model = telescope_config("pyuvsim", 2, 1, 1, 1, True)

uvd_out = uvsim.run_uvdata_uvsim(uvdata, BeamList(beam), beam_dict=beam_dict, catalog=simsetup.SkyModelData(sky_model))

sim_auto = uvd_out.get_data(0, 0, "XX")[0][0]
sim_cross = uvd_out.get_data(0, 1, "XX")[0][0]

print("pyuvsim -------------")
print("auto amp:", np.abs(sim_auto))
print("cross amp:", np.abs(sim_cross), "phase:", np.angle(sim_cross))

print("V",uvd_out.data_array)

# various versions of hera_sim

uvdata, beam, beam_dict, freqs, ra_dec, flux = telescope_config("hera_sim", 2, 1, 1, 1, True)

simulator = VisCPU_hugh(
    uvdata = uvdata,
    beams = beam,
    sky_freqs = freqs,
    point_source_pos = ra_dec,
    point_source_flux = flux,
    which = "astropy"
)

simulator.simulate()

sim_auto = simulator.uvdata.get_data(0, 0, "XX")[0][0]
sim_cross = simulator.uvdata.get_data(0, 1, "XX")[0][0]

print("hera_sim astropy ----")
print("auto amp:", np.abs(sim_auto))
print("cross amp:", np.abs(sim_cross), "phase:", np.angle(sim_cross))
print("V", simulator.uvdata.data_array)

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

print("hera_sim az_fix ----")
print("auto amp:", np.abs(sim_auto))
print("cross amp:", np.abs(sim_cross), "phase:", np.angle(sim_cross))
print("V",simulator.uvdata.data_array)
