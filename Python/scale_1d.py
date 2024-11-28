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
# -- ModuleName : scale_1d.py
# -- ModuleType : Example external command script for JASON 
# -- Purpose : External data processing in JASON 
# -- Date : November 2024 
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

import h5py
from argparse import ArgumentParser

import numpy as np


# Parse the commandline arguments

parser = ArgumentParser()
parser.add_argument("-f", "--filename", action="store")
parser.add_argument("-m", "--mode", action="store")
parser.add_argument("--value", action="store", default=1.0, type=float)
args = parser.parse_args()


# Open a file handle for the Jason datafile

f = h5py.File(args.filename, "r+")
print('Opening dataset: ', args.filename)


# Read the spectrum

dataset_real = f['JasonDocument/DataPoints/0'][()]
dataset_imag = f['JasonDocument/DataPoints/1'][()]


# Scale the spectrum

if (args.mode == 'sum'):
    dataset_real = dataset_real / np.sum(dataset_real)
    dataset_imag = dataset_imag / np.sum(dataset_imag)
    print('Dataset changed')

elif (args.mode == 'max'):
    dataset_real = dataset_real / np.max(dataset_real)
    dataset_imag = dataset_imag / np.max(dataset_imag)
    print('Dataset changed')

elif (args.mode == 'scale'):
    dataset_real = dataset_real * args.value
    dataset_imag = dataset_imag * args.value
    print('Dataset changed')

else:
    print('Unknown scaling operation, data not modified')


# Write back the processed dataset#

del f['/JasonDocument/DataPoints/0']
del f['/JasonDocument/DataPoints/1']
f.create_dataset('/JasonDocument/DataPoints/0', data=dataset_real)
f.create_dataset('/JasonDocument/DataPoints/1', data=dataset_imag)
f.close()
