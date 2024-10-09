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
# -- ModuleName : cadzow_denoising.py
# -- ModuleType : Example external command script for JASON 
# -- Purpose : Denoising of an FID via Cadzow (Henkel/SVD)
# -- Date : Oct 2024
# -- Author : Iain J. Day
# -- Language : Python
# -- 
# --##---------------------------------------------------------------------------
#
# This script implements Cadzow denoising of an FID
#
# How to use:
#  In JASON, add "External command" to the processing list, apply to the FID
#
#  Set for external command parameters:
#
#   Set "cmd" to "python" or to the full path to python.exe 
#     (e.g. C:\Program Files\Python311\python.exe)
#
#   Set "arguments" to the path of the script, specifying the use of a temporary 
#   file
#     (e.g. "C:\Users\<username>\.jason\externalNMRProcessing\python\direct_covariance.py -f $TMPFILE")
#     the -k (--kindex) option truncates the SVD after this number of singular values
#     the -i (--itr) option sets the number of smoothing iterations to apply, default = 2
#     the -p (--plot) option plots the signular values to help determine the truncation index
#     
#  Set "Data file" to "Spectrum as JJH5"
#
# Press "Apply"
#
# Reference: H. F. Cancino-De-Greiff, R. Ramos-Garcia, J. V. Lorenzo-Ginori, 
#  Concepts in Magnetic Resonance, 14(6), (2002), 388-401
#

import h5py
from argparse import ArgumentParser

import numpy as np
from scipy.linalg import diagsvd, hankel, svd

import matplotlib.pyplot as plt


# Parse the commandline arguments

parser = ArgumentParser()
parser.add_argument("-f", "--filename", action="store")
parser.add_argument("-k", "--kindex", action="store", type=int)
parser.add_argument("-i", "--itr", action="store", type=int, default=2)
parser.add_argument("-p", "--plot", action="store_true")

args = parser.parse_args()


# Open a file handle for the Jason datafile

f = h5py.File(args.filename, "r+")
print('Opening dataset: ', args.filename)


# Read the spectrum

dataset_real = f['JasonDocument/DataPoints/0'][()]
dataset_imag = f['JasonDocument/DataPoints/1'][()]
dataset = dataset_real + dataset_imag * 1j


# Apply the Cadzow denoising algorithm

if not args.itr % 2 != 1 or args.itr < 1:
    raise TypeError("number of iterations must be a positive even number")

n = len(dataset)
l = int(n / 2.0)
k = args.kindex

dataset_denoised = dataset.copy()

for it in range(args.itr):
    # Construct a Hankel matrix from the appropriately partitioned
    # input signal and calculate its SVD

    S = hankel(dataset_denoised[:l], dataset_denoised[l-1:])
    U, sigma, V = svd(S, full_matrices=False)


    # If reqested, plot the singular values for the first iteration to
    # aid in the choice of the cut off index k

    if args.plot and (it == 0):
        plt.figure(0)
        plt.plot(sigma)
        plt.xlabel('index, i')
        plt.ylabel('Singular Value, s_i')
        plt.title('Singular Value Spectrum for Cadzow denoising')
        plt.show()


    # Apply the threshold at index k, rebuilding a "cleaned" matrix
    # Flip left-right to allow easy access to antidiagonals

    S = np.dot(np.dot(U[:, :k], diagsvd(1.0 / sigma[:k], k, k)), V[:k, :])
    S = np.fliplr(S)


    # Average the diagonals to restore the Hankel structure of the
    # "cleaned" matrix, and store in a new signal array

    for i in range(n):
        j = n - l - i
        dataset_denoised[i] = sum(np.diag(S, k=j)) / len(np.diag(S, k=j))


# Write back the processed dataset#

del f['/JasonDocument/DataPoints/0']
del f['/JasonDocument/DataPoints/1']
f.create_dataset('/JasonDocument/DataPoints/0', data=dataset_denoised.real)
f.create_dataset('/JasonDocument/DataPoints/1', data=dataset_denoised.imag)
print('Dataset changed')
f.close()
