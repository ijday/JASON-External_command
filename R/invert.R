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
# -- ModuleName : invert.R
# -- ModuleType : Example external command script for JASON 
# -- Purpose : External data processing in JASON 
# -- Date : February 2023 
# -- Author : Iain J. Day
# -- Language : R
# -- 
# --##---------------------------------------------------------------------------
#
# A simple R script to invert spectrum point-by-point
#
# The rhdf5 library can be installed by running the following from the R prompt:
# > install.packages("BiocManager")
# > BiocManager::install("rhdf5")
# 
# How to use:
# In Jason, add "External command" to the processing list
# Set for external command parameters:
#  Set "cmd" to "R" or to the full path to Rscript.exe 
#     (e.g. C:\Program Files\R\R-4.2.1\bin\Rscript.exe)
#  Set "arguments" to the path of the script 
#     (e.g. "C:\Users\<username>\Desktop\invert.R")
#  Set "Data file" to "Spectrum as JJH5"
# Press "Apply"

library("rhdf5")

dataset = "/JasonDocument/DataPoints/"

args = commandArgs(trailingOnly=TRUE)
filename = args[1]

dsetre = h5read(filename, paste(dataset, "0", sep=""))
dsetim = h5read(filename, paste(dataset, "1", sep=""))

print(paste("dataset size:", length(dsetre)))
h5write(-dsetre, filename, paste(dataset, "0", sep=""))
h5write(-dsetim, filename, paste(dataset, "1", sep=""))

print("dataset changed")
