#! /usr/bin/env python

# ------------------------------------------------------------------------------- 
# --
# -- JEOL Ltd.
# -- 1-2 Musashino 3-Chome
# -- Akishima Tokyo 196-8558 Japan 
# -- Copyright 2024 
# -- 
#
# --++--------------------------------------------------------------------------- 
# -- 
# -- ModuleName : JASON
# -- ModuleType : Example external command script for JASON 
# -- Purpose : desktop software 
# -- Date : Oct 2024
# -- Author : Peter Kiraly / Iain J. Day
# -- Language : Python
# -- 
# --##---------------------------------------------------------------------------
#
# This script enables editing the nuslist for NUS datasets
#
# How to use:
#  In JASON, add "External command" to the processing list
# 
#  Set for external command parameters:
#
#   Set "cmd" to "python" or to the full path to python.exe 
#     (e.g. C:\Program Files\Python311\python.exe)
#
#   Set "arguments" to the path of the script, specifying the use of a temporary 
#   file
#     (e.g. "C:\Users\<username>\.jason\externalNMRProcessing\python\jasonParEdit.py -f $TMPFILE")
#     use the -l flag to set the name of a file containing the new nuslist as a point per line
#     
#  Set "Data file" to "Spectrum as JJH5"
#
# Press "Apply"
#

import h5py
from argparse import ArgumentParser
import numpy as np

# Process commandline options
parser = ArgumentParser()
# temporary file name
parser.add_argument("-f", "--filename", action="store")
# parameter name
parser.add_argument("-l", "--list", action="store")

args = parser.parse_args()

# Open a file handle for the JASON datafile
f = h5py.File(args.filename, "r+")
print('Opening dataset: ', args.filename)

# checks if attribute exists in the file
keys = f['JasonDocument/SpecInfo/lists'].attrs.keys()
if 'nuslist' in keys:
    newnuslist = np.genfromtxt(args.list, delimiter=' ', dtype=float)
    f['JasonDocument/SpecInfo/lists'].attrs.modify('nuslist', newnuslist)
    print('NUS List updated')

else:
    print('Error: nuslist does not exist.')            

f.close()
