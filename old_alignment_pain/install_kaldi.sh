#!/bin/bash

# Prepare Kaldi
# ../../ because this file install_kaldi.sh is also 
# copied in from elsewhere...
cp ../../kaldi_tools_Makefile.mod kaldi/tools/Makefile
cd kaldi/tools
make atlas openfst OPENFST_VERSION=1.4.1
#make openblas openfst OPENFST_VERSION=1.6.0
#make openblas openfst OPENFST_VERSION=1.4.1
#--openblas-root=../tools/OpenBLAS/install
cd ../src
#OPENFST_VER=1.4.1 ./configure --static --static-math=yes --static-fst=yes --use-cuda=no #--openblas-root=../tools/OpenBLAS/install
OPENFST_VER=1.4.1 ./configure --static --static-math=yes --static-fst=yes --use-cuda=no #--openblas-root=../tools/OpenBLAS/install
# /usr/lib/x86_64-linux-gnu/
# manually hack in and find/replace lib path! this is.... sketchy
sed -i -e "s|\[somewhere\]|/usr/lib/x86_64-linux-gnu/|g" kaldi.mk
make depend
cd ../../
