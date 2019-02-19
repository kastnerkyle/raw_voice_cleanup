set -e
# may not be necessary in general but I needed to avoid sudo
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:"~/anaconda/lib"
export CXX=g++-6
export CC=gcc-6

if [ ! -d gentle ]; then
  git clone https://github.com/kastnerkyle/gentle
fi

cd gentle
git checkout tags/0.10.1
git submodule init
git submodule update
cp ../install_kaldi.sh ext/install_kaldi.sh
cd ext && bash install_kaldi.sh
cd ..
bash install_models.sh
cd ext && make depend && make
