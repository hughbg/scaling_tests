from hera_sim import io
from hera_sim.beams import PerturbedPolyBeam
from astropy.coordinates import Latitude, Longitude
from astropy.units import Quantity
import numpy as np
from pyuvsim.telescope import BeamList
from pyuvsim import AnalyticBeam
from pyradiosky import SkyModel
#import healvis as hv

originals = True   # Run the vanilla codes

def telescope_config(which_package, nant=2, nfreq=2, ntime=1, nsource=1, simple_beam=False):
    """
    Setup the configuration parameters for pyuvsim/hera_sim/healvis.
    Different packages require different objects for simulation.
    """
    if which_package not in [ "hera_sim", "pyuvsim", "healvis" ]:
        raise ValueError("Unknown package: "+which_package)
        
    np.random.seed(10)          # So we always get the same random values

    # Random antenna locations
    x = np.random.random(nant)*400     # Up to 400 metres
    y = np.random.random(nant)*400
    z = np.random.random(nant)
    ants = {}
    for i in range(nant):
        ants[i] = ( x[i], y[i], z[i] )
        
    # Observing parameters in a UVData object.
    uvdata = io.empty_uvdata(
        Nfreqs = nfreq,             # Need 2 freqs for healvis to work
        start_freq = 100e6,
        channel_width = 97.3,
        start_time = 2458902.4,
        integration_time = 40.0,
        Ntimes = ntime,
        array_layout = ants,
        polarization_array = np.array([ "XX", "YY", "XY", "YX" ]),
        Npols = 4
    )
    
    # Random sources.
    sources = [
        [ 125.7, -30.72, 2, 0 ],     # Source near zenith, which is at 130.7   -30.72
        ]
    if nsource > 1:
        ra = 100+np.random.random(nsource-1)*50
        dec = -10.72+np.random.random(nsource-1)*40
        flux = np.random.random(nsource-1)*4
        for i in range(nsource-1): sources.append([ ra[i], dec[i], flux[i], 0])
    sources = np.array(sources)

    # Source locations and frequencies.
    ra_dec = np.deg2rad(sources[:, :2])
    freqs = np.unique(uvdata.freq_array)

    if which_package == "hera_sim":
        # calculate source fluxes for hera_sim. pyuvsim does it a different way.
        flux = (freqs[:,np.newaxis]/freqs[0])**sources[:,3].T*sources[:,2].T      
        beam_ids = list(ants.keys())

    if simple_beam:
        beam = [AnalyticBeam("gaussian", sigma=0.103) for i in range(len(ants.keys()))]
    else:
        # Beam model. PerturbedPolyBeam, which is not symmetrical.
        cfg_beam = dict(ref_freq=1.e8,
            spectral_index =        -0.6975,
            mainlobe_width =        0.3 ,
            beam_coeffs=[ 0.29778665, -0.44821433, 0.27338272, 
                                  -0.10030698, -0.01195859, 0.06063853, 
                                  -0.04593295,  0.0107879,  0.01390283, 
                                  -0.01881641, -0.00177106, 0.01265177, 
                                  -0.00568299, -0.00333975, 0.00452368,
                                   0.00151808, -0.00593812, 0.00351559
                                 ] )

        beam = [PerturbedPolyBeam(np.array([-0.20437532, -0.4864951,  -0.18577532, -0.38053642,  0.08897764,  0.06367166,
                              0.29634711,  1.40277112]),
                              mainlobe_scale=1.0, xstretch=0.9, ystretch=0.8, **cfg_beam) 
                for i in range(len(ants.keys()))]

    beam_dict = {}
    for i in range(len(beam)): beam_dict[str(i)] = i

    # That's enough for hera_sim, but extra objects are required for pyuvsim and healvis.
    
    if which_package == "pyuvsim":
        # Need a sky model.
        
        # Stokes for the first frequency only. Stokes for other frequencies
        # are calculated later.
        stokes = np.zeros((4, 1, ra_dec.shape[0]))
        stokes[0, 0] = sources[:, 2]
        reference_frequency = np.full(len(ra_dec), freqs[0])
        
        # Setup sky model.
        sky_model = SkyModel(name=[ str(i) for i in range(len(ra_dec)) ],
            ra=Longitude(ra_dec[:, 0], "rad"), dec=Latitude(ra_dec[:, 1], "rad"),
            spectral_type="spectral_index",
            spectral_index=sources[:,3],
            stokes =stokes,
            reference_frequency=Quantity(reference_frequency, "Hz")
            )

        # Calculate stokes at all the frequencies.
        sky_model.at_frequencies(Quantity(freqs, "Hz"), inplace=True)
        
    if which_package == "healvis":
        # Need a GSM model and an Observatory.
        
        baselines = []
        for i in range(len(ants)):
            for j in range(i+1, len(ants)):
                if originals:
                    bl = hv.observatory.Baseline(ants[i], ants[j])
                else:
                    bl = hv.observatory.Baseline(ants[i], ants[j], i, j)
                baselines.append(bl)

        times = np.unique(uvdata.get_times("XX"))

        obs_latitude=-30.7215277777
        obs_longitude = 21.4283055554
        obs_height = 1073

        # create the observatory
        fov = 360  # Deg
        if originals:
            obs = hv.observatory.Observatory(obs_latitude, obs_longitude, array=baselines, freqs=freqs)
        else:
            obs = hv.observatory.Observatory(obs_latitude, obs_longitude, obs_height, array=baselines, freqs=freqs)
        obs.set_pointings(times)
        obs.set_fov(fov)
        if originals:
            obs.set_beam("gaussian", gauss_width=0.103)
        else:
            obs.set_beam(beam)

        gsm = hv.sky_model.construct_skymodel('gsm', freqs=freqs, Nside=32)
    
    
        
    # Return what is relevant for each package, pyuvsim or hera_sim
    if which_package == "hera_sim":
        return uvdata, beam, beam_dict, freqs, ra_dec, flux
    elif which_package == "pyuvsim":
        return uvdata, beam, beam_dict, sky_model
    elif which_package == "healvis":
        return obs, gsm
