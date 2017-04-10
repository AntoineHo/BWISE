#!/bin/bash

# Script to compile BWise source code and all its dependencies from
# their respective project. 
#
# It requires a c++/11 aware compiler; e.g. gcc 4.8+ (Linux) or Apple/clang 6+ (OSX),
# as well as git and cmake 3.1+.
#

function help {
echo "BWISE installation script"
echo "This installation requires GCC>=4.9, GIT, MAKE and CMAKE3 and Python3"
echo "-f absolute path of folder to put the binaries"
echo "-t to use multiple thread for compilation (default 8)"
}

# Default values for arguments
threadNumber=8
SCRIPT_DIR=$( cd -P -- "$(dirname -- "$(command -v -- "$0")")" && pwd -P )
BIN_DIR=${SCRIPT_FOLDER}/bin

# Handle command-line arguments
while getopts "hf:t:" opt; do
case $opt in
h)
help
exit
;;
f)
echo "use folder: $OPTARG" >&2
BIN_DIR=$OPTARG
;;
t)
echo "use  $OPTARG threads" >&2
threadNumber=$OPTARG
;;
\?)
echo "Invalid option: -$OPTARG" >&2
exit 1
;;
:)
echo "Option -$OPTARG requires an argument." >&2
exit 1
;;
esac
done

# No build directory? Error.
if [ -z "$BIN_DIR"  ]; then
	help
	exit 0
	fi

# make the build directory if it does not exist
mkdir -p $BIN_DIR;
echo "All binaries will be placed in: $BIN_DIR";

# switch to source directory and make the entire build: BWISE and all
# its dependencies
cd src;

make LOL=-Dfolder=$BIN_DIR -j $threadNumber >>logCompile 2>>logCompile;
cp bwise ..;
cp K2000/*.py $BIN_DIR;
cp sequencesToNumbers $BIN_DIR;
cp numbersFilter $BIN_DIR;
cp numbersToSequences $BIN_DIR;
echo PHASE ZERO LAUNCHER: BWISE;

echo "Clone Bloocoo"
git clone --recursive https://github.com/GATB/bloocoo.git >>logCompile 2>>logCompile;
cd bloocoo;
echo "Make Bloocoo-32"
mkdir build32; cd build32;
cmake -DKSIZE_LIST="32" .. >>logCompile 2>>logCompile;
make -j $threadNumber >>logCompile 2>>logCompile;
cp bin/Bloocoo Bloocoo32;
cp Bloocoo32 $BIN_DIR;
cd ..;
echo "Make Bloocoo-64"
mkdir build64; cd build64;
cmake -DKSIZE_LIST="64" .. >>logCompile 2>>logCompile;
make -j $threadNumber >>logCompile 2>>logCompile;
cp bin/Bloocoo Bloocoo64;
cp Bloocoo64 $BIN_DIR;
cd ..;
echo "Make Bloocoo-128"
mkdir build128; cd build128;
cmake -DKSIZE_LIST="128" .. >>logCompile 2>>logCompile;
make -j $threadNumber >>logCompile 2>>logCompile;
cp bin/Bloocoo Bloocoo128;
cp Bloocoo128 $BIN_DIR;
cd ../..;
#~ cp bloocoo/build32/ext/gatb-core/bin/h5dump $BIN_DIR;

echo "Clone/Make Bcalm-32 64 128 160 224 256 320 512 1024"
git clone --recursive https://github.com/GATB/bcalm >>logCompile 2>>logCompile;
cd bcalm;
mkdir build; cd build;
cmake -DKSIZE_LIST="32 64 128 160 224 256 320 512 1024"  ..  >>logCompile 2>>logCompile;
make -j $threadNumber >>logCompile 2>>logCompile;
cp bcalm $BIN_DIR;
cd ../..;

echo "Clone/Make BGreat"
git clone https://github.com/Malfoy/BGREAT2 >>logCompile 2>>logCompile;
cd BGREAT2;
make -j $threadNumber >>logCompile 2>>logCompile;
cp bgreat $BIN_DIR;
cd ..;

#~ git clone --recursive https://github.com/Malfoy/BREADY >>logCompile 2>>logCompile;
#~ cd BREADY;
#~ mkdir build; cd build;
#~ cmake .. >>logCompile 2>>logCompile;
#~ make -j $threadNumber >>logCompile 2>>logCompile;
#~ cp bin/BREADY $BIN_DIR;
#~ cd ../..;
#~ git clone --recursive https://github.com/GATB/dsk.git >>logCompile 2>>logCompile;
#~ cd dsk;
#~ mkdir build;  cd build;
#~ cmake -DKSIZE_LIST="32" .. >>logCompile 2>>logCompile;
#~ make -j $threadNumber >>logCompile 2>>logCompile;
#~ cp bin/dsk $BIN_DIR;
#~ cd ../..;
#~ echo PHASE FOUR, SUPERREADS CLEANING: BREADY;

echo "Clone/Make kMill"
git clone https://github.com/kamimrcht/kMILL >>logCompile 2>>logCompile;
cd kMILL/src;
make -j $threadNumber >>logCompile 2>>logCompile;
cp kMILL $BIN_DIR;
cp sequencesCleaner $BIN_DIR;
cp tipCleaner $BIN_DIR;
cd ../..;

echo "DONE: 'bwise' binary available in $SCRIPT_FOLDER"
