#!/bin/bash

# How many correction steps
COR=2

# Prepare a fresh working directory
DIRECTORY=folderTest
if [ -d $DIRECTORY ]; then
  rm -rf $DIRECTORY
fi

# Start BWise (it creates $DIRECTORY)
../Bwise.py -x examplePairedReads.fa -u exampleUnpairedReads.fa  -o $DIRECTORY -c $COR

# Test ok?
if [ -f "$DIRECTORY/compacted_unitigs_k51.fa" ];
then
  echo "IT WORKS !";
  ../build/n50 $DIRECTORY/compacted_unitigs_k51.fa  ;
else
   echo "FAIL"
fi

