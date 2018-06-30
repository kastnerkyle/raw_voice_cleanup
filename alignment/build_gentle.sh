set -e
# may not be necessary in general but I needed to avoid sudo
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:"~/anaconda/lib"

git clone https://github.com/kastnerkyle/gentle
#git clone https://github.com/lowerquality/gentle

cd gentle
git checkout tags/0.10.1
git submodule init
git submodule update
cp ../install_kaldi.sh ext/install_kaldi.sh
cd ext && bash install_kaldi.sh
cd ..
bash install_models.sh
cd ext && make depend && make
