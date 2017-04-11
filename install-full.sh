#!/bin/bash

# Script to compile BWise source code and all its dependencies from
# their respective project. 
#
# Compiling BWISE requires a c++/11 aware compiler; e.g. gcc 4.8+ (Linux) or 
# Apple/clang 6+ (OSX) as well as Python 3. 
#
# Git and CMake (3.1+) are also required.
#

function help {
echo "BWISE installation script"
echo "This installation requires GCC>=4.9, GIT, MAKE and CMAKE3 and Python3"
echo "-f absolute path of folder to put the binaries"
echo "-t to use multiple thread for compilation (default 8)"
}

# Default values for arguments
threadNumber=4
SCRIPT_DIR=$( cd -P -- "$(dirname -- "$(command -v -- "$0")")" && pwd -P )
BUILD_DIR=${SCRIPT_DIR}/build

# Handle command-line arguments
while getopts "hf:t:" opt; do
case $opt in
h)
help
exit
;;
f)
echo "INFO: use folder: $OPTARG" >&2
BUILD_DIR=$OPTARG
;;
t)
echo "INFO: use $OPTARG threads" >&2
threadNumber=$OPTARG
;;
\?)
echo "ERROR: Invalid option: -$OPTARG" >&2
exit 1
;;
:)
echo "ERROR: Option -$OPTARG requires an argument." >&2
exit 1
;;
esac
done

# No build directory? Error.
if [ -z "$BUILD_DIR"  ]; then
	help
	exit 0
	fi

# make the build directory if it does not exist
mkdir -p $BUILD_DIR;
echo "INFO: all binaries will be placed in: $BUILD_DIR";

# switch to source directory and make the entire build: BWISE and all
# its dependencies
cd ${SCRIPT_DIR}/src;

echo "INFO: compiling BWISE..."
make LOL=-Dfolder=$BUILD_DIR -j $threadNumber >>logCompile 2>>logCompile;
cp bwise ..;
cp K2000/*.py $BUILD_DIR;
cp sequencesToNumbers $BUILD_DIR;
cp numbersFilter $BUILD_DIR;
cp numbersToSequences $BUILD_DIR;
cp n50 $BUILD_DIR

echo ""
echo "INFO: cloning Bloocoo..."
git clone --recursive https://github.com/GATB/bloocoo.git >>logCompile 2>>logCompile;
cd bloocoo;
echo "INFO: compiling Bloocoo-32..."
mkdir build32; cd build32;
cmake -DKSIZE_LIST="32" .. >>logCompile 2>>logCompile;
make -j $threadNumber >>logCompile 2>>logCompile;
cp bin/Bloocoo Bloocoo32;
cp Bloocoo32 $BUILD_DIR;
cd ..;
echo "INFO: compiling Bloocoo-64..."
mkdir build64; cd build64;
cmake -DKSIZE_LIST="64" .. >>logCompile 2>>logCompile;
make -j $threadNumber >>logCompile 2>>logCompile;
cp bin/Bloocoo Bloocoo64;
cp Bloocoo64 $BUILD_DIR;
cd ..;
echo "INFO: compiling Bloocoo-128..."
mkdir build128; cd build128;
cmake -DKSIZE_LIST="128" .. >>logCompile 2>>logCompile;
make -j $threadNumber >>logCompile 2>>logCompile;
cp bin/Bloocoo Bloocoo128;
cp Bloocoo128 $BUILD_DIR;
cd ../..;
#~ cp bloocoo/build32/ext/gatb-core/bin/h5dump $BUILD_DIR;

echo ""
echo "INFO: cloning Bclam..."
git clone --recursive https://github.com/GATB/bcalm >>logCompile 2>>logCompile;
cd bcalm;
echo "INFO: compiling Bcalm-32 64 128 160 224 256 320 512 1024..."
mkdir build; cd build;
cmake -DKSIZE_LIST="32 64 128 160 224 256 320 512 1024"  ..  >>logCompile 2>>logCompile;
make -j $threadNumber >>logCompile 2>>logCompile;
cp bcalm $BUILD_DIR;
cd ../..;

echo ""
echo "INFO: cloning BGREAT2..."
git clone https://github.com/Malfoy/BGREAT2 >>logCompile 2>>logCompile;
cd BGREAT2;
echo "INFO: compiling BGREAT2..."
make -j $threadNumber >>logCompile 2>>logCompile;
cp bgreat $BUILD_DIR;
cd ..;

#~ git clone --recursive https://github.com/Malfoy/BREADY >>logCompile 2>>logCompile;
#~ cd BREADY;
#~ mkdir build; cd build;
#~ cmake .. >>logCompile 2>>logCompile;
#~ make -j $threadNumber >>logCompile 2>>logCompile;
#~ cp bin/BREADY $BUILD_DIR;
#~ cd ../..;
#~ git clone --recursive https://github.com/GATB/dsk.git >>logCompile 2>>logCompile;
#~ cd dsk;
#~ mkdir build;  cd build;
#~ cmake -DKSIZE_LIST="32" .. >>logCompile 2>>logCompile;
#~ make -j $threadNumber >>logCompile 2>>logCompile;
#~ cp bin/dsk $BUILD_DIR;
#~ cd ../..;
#~ echo PHASE FOUR, SUPERREADS CLEANING: BREADY;

echo ""
echo "INFO: cloning kMILL..."
git clone https://github.com/kamimrcht/kMILL >>logCompile 2>>logCompile;
cd kMILL/src;
echo "INFO: compiling kMILL..."
make -j $threadNumber >>logCompile 2>>logCompile;
cp kMILL $BUILD_DIR;
cp sequencesCleaner $BUILD_DIR;
cp tipCleaner $BUILD_DIR;
cd ../..;

echo "DONE: 'bwise' binary available in $SCRIPT_FOLDER"
