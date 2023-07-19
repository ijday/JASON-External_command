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
# -- ModuleName : invert.py
# -- ModuleType : Example external command script for JASON 
# -- Purpose : External data processing in JASON 
# -- Date : February 2023 
# -- Author : Iain J. Day
# -- Language : Python
# -- 
# --##---------------------------------------------------------------------------
#
# A simple Python script to invert spectrum point-by-point
# How to use:
# In Jason, add "External command" to the processing list
# Set for external command parameters:
#  Set "cmd" to "python" or to the full path to python.exe 
#     (e.g. C:\Program Files\Python311\python.exe)
#  Set "arguments" to the path of the script 
#     (e.g. "C:\Users\<username>\Desktop\invert.py")
#  Set "Data file" to "Spectrum as JJH5"
# Press "Apply"

import sys
import h5py
import numpy as np

with h5py.File(sys.argv[1], "r+") as hf:
    print("Opening dataset:", sys.argv[1])
    dsetre = hf['/JasonDocument/DataPoints/0']
    dsetim = hf['/JasonDocument/DataPoints/1']
    print("dataset size:", len(dsetre))
    dsetre[...]=np.negative(dsetre)
    dsetim[...]=np.negative(dsetim)
    print("dataset changed")
    hf.close()
    