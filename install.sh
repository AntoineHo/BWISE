#!/bin/bash

# Script to compile BWise source code only.
#
# BWISE dependencies are retrieved from 'bin' directory which contains pre-compiled
# binaries for Linux and OSX.
#
# Compiling BWISE requires a c++/11 aware compiler; e.g. gcc 4.8+ (Linux) or 
# Apple/clang 6+ (OSX) as well as Python 3.
#

function help {
  echo "BWISE installation script"
  echo "This installation requires GCC>=4.9 (Linux) or Apple/clang 6 (OSX) and Python3"
  echo "-t to use multiple thread for compilation (default 8)"
}

threadNumber=8

while getopts "ht:" opt; do
case $opt in
h)
help
exit
;;
t)
echo "INFO: will use $OPTARG threads" >&2
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

SCRIPT_FOLDER=$( cd -P -- "$(dirname -- "$(command -v -- "$0")")" && pwd -P )
OS_NAME=`uname -a | cut -d' ' -f 1`

# we prepare the build directory
SRC_DIR=${SCRIPT_FOLDER}/src
BUILD_DIR=${SCRIPT_FOLDER}/build
[ -d $BUILD_DIR  ] && { rm -rf $BUILD_DIR ; }
mkdir $BUILD_DIR

if [ $OS_NAME == "Linux" ]; then
  BIN_FOLDER=${SCRIPT_FOLDER}/bin/linux
elif [ $OS_NAME == "Darwin" ]; then
  BIN_FOLDER=${SCRIPT_FOLDER}/bin/osx
else
  echo "ERROR: unsupported platform: $OS_NAME"
  exit 1
fi

echo " "
echo "INFO: BWISE-dep binaries transfered from: '$BIN_FOLDER' to: '$BUILD_DIR'"

cp $BIN_FOLDER/* $BUILD_DIR

echo " "
echo "INFO: Compiling BWISE..."

# switch to source folder
cd $SRC_DIR
# we prepare a clean make 
make clean > logCompile 2>&1
# we compile BWISE only
make LOL=-Dfolder=$BUILD_DIR -j $threadNumber >> logCompile 2>&1
# ok?
[ "$?" -ne 0 ] && { echo "ERROR: make failed. Check and fix errors reported in: ${SRC_DIR}/logCompile" ; exit 1 ; }

# prepare bin folder
cp bwise ..
cp K2000/*.py $BUILD_DIR
cp sequencesToNumbers $BUILD_DIR
cp numbersFilter $BUILD_DIR
cp numbersToSequences $BUILD_DIR
cp n50 $BUILD_DIR
make clean >> logCompile 2>&1

echo "INFO: bwise binary available in $SCRIPT_FOLDER"

