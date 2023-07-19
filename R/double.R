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
# -- ModuleName : double.R
# -- ModuleType : Example external command script for JASON 
# -- Purpose : External data processing in JASON 
# -- Date : February 2023 
# -- Author : Iain J. Day
# -- Language : R
# -- 
# --##---------------------------------------------------------------------------
#
# A simple R script to double the processed spectrum by appending inverted 
# spectrum at the end
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
#     (e.g. "C:\Users\<username>\Desktop\double.R")
#  Set "Data file" to "Spectrum as JJH5"
# Press "Apply"

library("rhdf5")

dataset = "/JasonDocument/DataPoints/"

args = commandArgs(trailingOnly=TRUE)
filename = args[1]

dsetre = h5read(filename, paste(dataset, "0", sep=""))
dsetim = h5read(filename, paste(dataset, "1", sep=""))
dattrs = h5readAttributes(filename, "/JasonDocument")
dlength = dattrs[['Length']][1]

print(paste("dataset initial size:", dlength))

dsetre = append(dsetre, -dsetre)
dsetim = append(dsetim, -dsetim)
dlength <- 2.0 * dlength
dattrs[['Length']][1] <- dlength
print(paste("dataset new size:", dlength))

h5delete(filename, paste(dataset, "0", sep=""))
h5delete(filename, paste(dataset, "1", sep=""))
h5write(dsetre, filename, paste(dataset, "0", sep=""))
h5write(dsetim, filename, paste(dataset, "1", sep=""))

fileid = H5Fopen(filename)
groupid = H5Gopen(fileid, "/JasonDocument")
h5writeAttribute(as.integer(dattrs[['Length']]), groupid, 'Length')
H5Gclose(groupid)
H5Fclose(fileid)

print("dataset changed")
