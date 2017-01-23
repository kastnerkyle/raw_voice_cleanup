#!/bin/bash

# Prepare Kaldi
cd kaldi/tools
#make atlas openfst OPENFST_VERSION=1.4.1
make openblas openfst OPENFST_VERSION=1.4.1
#--openblas-root=../tools/OpenBLAS/install
cd ../src
./configure --static --static-math=yes --static-fst=yes --use-cuda=no --openblas-root=../tools/OpenBLAS/install
make depend
cd ../../
