#! /usr/bin/env python

# ------------------------------------------------------------------------------- 
# --
# -- JEOL Ltd.
# -- 1-2 Musashino 3-Chome
# -- Akishima Tokyo 196-8558 Japan 
# -- Copyright 2022 
# -- 
#
# --++--------------------------------------------------------------------------- 
# -- 
# -- ModuleName : direct_covariance.py
# -- ModuleType : Example external command script for JASON 
# -- Purpose : Direct Covariance processing via external data processing in JASON 
# -- Date : Oct 2024
# -- Author : Iain J. Day
# -- Language : Python
# -- 
# --##---------------------------------------------------------------------------

import sys
import h5py
from argparse import ArgumentParser

import numpy as np
from scipy.linalg import sqrtm


# Parse the commandline arguments

parser = ArgumentParser()
parser.add_argument("-f", "--filename", action="store")
parser.add_argument("-n", "--nosqrt", action="store_false")
args = parser.parse_args()


# Open a file handle for the Jason datafile

f = h5py.File(args.filename, "r+")
print('Opening dataset: ', args.filename)


# Read the real part of the spectrum

dataset = f['JasonDocument/DataPoints/0'][()]


# Get some parameters associated with the spectrum

length = f['JasonDocument/'].attrs['Length']
sw = f['JasonDocument/SpecInfo'].attrs['SW']
spec_freq = f['JasonDocument/SpecInfo'].attrs['SpectrometerFrequencies']
spec_ref = f['JasonDocument/SpecInfo'].attrs['SpectrumRef']


# Calculate the direct covariance (S.T . S)

covar = np.dot(dataset.T, dataset)

if args.nosqrt:
    covar = sqrtm(covar)
    covar = covar.real


# Update parameters

length[1] = covar.shape[0]
sw[1] = sw[0]
spec_freq[1] = spec_freq[0]
spec_ref[1] = spec_ref[0]
f['JasonDocument/'].attrs.modify('Length', length)
f['JasonDocument/SpecInfo'].attrs.modify('SW', sw)
f['JasonDocument/SpecInfo'].attrs.modify('SpectrometerFrequencies', spec_freq)
f['JasonDocument/SpecInfo'].attrs.modify('SpectrumRef', spec_ref)


# Write back the processed dataset#

del f['/JasonDocument/DataPoints/0']
f.create_dataset('/JasonDocument/DataPoints/0', data=covar)
print('Dataset changed')
f.close()
