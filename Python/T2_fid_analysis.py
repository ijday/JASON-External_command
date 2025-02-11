#!python3

# ------------------------------------------------------------------------------- 
# --
# -- JEOL Ltd.
# -- 1-2 Musashino 3-Chome
# -- Akishima Tokyo 196-8558 Japan 
# -- Copyright 2023 
# -- 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# --++--------------------------------------------------------------------------- 
# -- 
# -- ModuleName : T2_fid_analysis.py
# -- ModuleType : Example external command script for JASON 
# -- Purpose : External data processing in JASON 
# -- Date : December 2024 
# -- Author : Iain J. Day
# -- Language : Python
# -- 
# --##---------------------------------------------------------------------------
#
# A simple Python script to vertically scale spectrum 
#
# How to use:
# In Jason, add "External command" to the processing list
#
# Set for external command parameters:
#
#  Set "cmd" to "python" or to the full path to python.exe 
#     (e.g. C:\Program Files\Python311\python.exe)
#
#   Set "arguments" to the path of the script, specifying the use of a temporary 
#   file
#     (e.g. "C:\Users\<username>\.jason\externalNMRProcessing\python\scale_1d.py -f $TMPFILE -m <MODE> [--scale <VALUE>])
#
# Press "Apply"

import sys
import h5py

import numpy as np
import matplotlib.pyplot as plt

from numpy.random import randn
from scipy.optimize import leastsq
from scipy.fft import fft, ifft, fftshift

from daylab.relaxation import spinecho, residuals_spinecho


# Open a file handle for the Jason datafile

f = h5py.File(sys.argv[1], "r+")
print('Opening dataset: ', sys.argv[1])


# Read the spectrum

dataset_real = f['JasonDocument/DataPoints/0'][()]
dataset_imag = f['JasonDocument/DataPoints/1'][()]


# Get some parameters from the data

npts = f['JasonDocument'].attrs['Length'][0]
sw = f['JasonDocument']['SpecInfo'].attrs['SW'][0]
sfrq = f['JasonDocument/SpecInfo'].attrs['SpectrometerFrequencies'][0]
sref = f['JasonDocument/SpecInfo'].attrs['SpectrumRef'][0]

dw = 1.0 / sw
sw = sw / sfrq
x_offset = sref / sfrq
sp = x_offset - sw / 2.0


multiplets = f['JasonDocument']['Multiplets_Integrals']['MultipletList'].values()

nmultiplets = len(multiplets)

xRange = []

for peak in multiplets:
    # Extract peak of interest

    integral = peak.attrs['SpectrumRange[0]']

    intpos = integral.mean()
    intlimit = np.array(npts * (integral - sp) / sw, dtype=int)
    
    if intlimit[0] < 1:
        intlimit[0] = 1

    if intlimit[1] > npts:
        intlimit[1] = npts

    intlimit = npts - intlimit

    spec = dataset_real.copy()

    spec[:intlimit[1]] = 0.0
    spec[intlimit[0]:] = 0.0


    # Shift to zero frequency and iFFT

    peak_max_idx = spec.argmax()
    spec = np.roll(spec, npts//2 - peak_max_idx - 1)

    fid = ifft(np.flipud(fftshift(spec, 0)), npts)
    fid = fid[:npts//2]
    fid = fid.real


    # Fit the FID

    fix0 = []
    p1 = np.zeros(3)
    time_pts = np.linspace(0, npts//2*dw, npts//2)

    p0 = [fid.max(), 1.0]

    p1, success = leastsq(residuals_spinecho, p0.copy(), \
        args=(fix0, time_pts, fid))


    # Determine the fitting error by Monte-Carlo

    mc_errors = np.zeros(2)
    num_mc = 1000

    if num_mc > 0:
        sigma = np.std(residuals_spinecho(p1, fix0, time_pts, fid))

        mocked_parameters = np.zeros((num_mc, 2), dtype=float)

        for i in range(num_mc):
            mock_data =spinecho(p1, fix0, time_pts) + sigma \
                * randn(len(time_pts))
            p2, success = leastsq(residuals_spinecho, p1.copy(), \
                args=(fix0, time_pts, mock_data))
            mocked_parameters[i, :] = p2

        mc_errors = np.std(mocked_parameters, axis=0)


    # Plot the results

    plt.plot(time_pts, fid)
    plt.plot(time_pts, spinecho(p1, fix0, time_pts))

    plt.title('FID envelope fit at {label:.2f} ppm'.format(label=intpos))
    plt.xlabel('Time / s')
    plt.ylabel('FID Intensity / a.u.')

    plt.annotate('$T_2$ = {label:.2f} +/- {labelerr:.3f} s'\
        .format(label=p1[1],  labelerr=mc_errors[1]), (0.65, 0.75), \
        xycoords='axes fraction')
    plt.annotate('$R_2$ = {label:.2f} +/- {labelerr:.3f} Hz'\
        .format(label=1.0 / p1[1],  labelerr=mc_errors[1] / p1[1]**2), (0.65, 0.70), \
        xycoords='axes fraction')
    plt.annotate('$LW$ = {label:.2f} +/- {labelerr:.3f} Hz'\
        .format(label=1.0 / (np.pi * p1[1]),  labelerr=mc_errors[1] / (np.pi * p1[1]**2)), (0.65, 0.65), \
        xycoords='axes fraction')

    plt.show()



# Write back the processed dataset

f.close()
