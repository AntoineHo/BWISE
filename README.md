[![Build Status](https://ci.inria.fr/gatb-core/view/BWISE/job/bwise-build-gcc48/2/badge/icon)](https://ci.inria.fr/gatb-core/view/BWISE/job/bwise-build-gcc48/2/) on Linux &nbsp;&nbsp;&nbsp; [![Build Status](https://ci.inria.fr/gatb-core/view/BWISE/job/bwise-build-clang6/badge/icon)](https://ci.inria.fr/gatb-core/view/BWISE/job/bwise-build-clang6/) on MacOSX

[![License](http://img.shields.io/:license-Affero--GPL-blue.svg)](http://www.gnu.org/licenses/agpl-3.0.en.html)

## BWISE

de Bruijn Workflow using Integral information of Short paired-End reads

**Work in progress** -- so far, this assembler was only tested with > 100X of 2*250 bp Illumina reads (recommended fragment library size ~500-600 bp). 

## Project structure

This project contains the source code of BWISE. It is organized as follows:

```
<BWISE-home>
   |
   |- bin: pre-compiled Linux/OSX binaries of BWISE dependencies
   |- data: small test suite
   |- docker: Docker file to create a BWISE container
   |- src: BWISE source code
   |
   |- build: created by install.sh scripts when compiling BWISE
```

In addition, ```<BWISE-home>``` contains several ```install.sh``` scripts that can be used to compile BWISE and prepare its associated ```build``` directory.
 
## INSTALLATION

BWISE relies on several third-party tools: [BGREAT2](https://github.com/Malfoy/BGREAT2), [BCALM](https://github.com/GATB/bcalm), [Bloocoo](https://github.com/GATB/bloocoo) and [kMILL](https://github.com/kamimrcht/kMILL). 

The software comes with pre-compiled versions of them for Linux and Mac OSX; they are located in the ```bin``` directory of this project. So, you have three options to install BWISE:

* using provided third-party tool binaries; this option can be used only if provided
binaries are compatible with your system;
* compiling the entire software stack, otherwise;
* in case software compiling process fails, you have the option to make a Docker container.

### Checking provided binaries

**Linux users:**

```bash
cd <BWISE-home>
cd bin/linux
./Bloocoo32

```

You should see ```Bloocoo``` help on the command line if ```Bloocoo32``` is compatible with your system. In such a case, use ```install.sh``` script to compile BWISE on your system; see below.

**MacOSX users:**

```bash
cd <BWISE-home>
cd bin/osx
./Bloocoo32

```

You should see ```Bloocoo``` help on the command line if ```Bloocoo32``` is compatible with your system. In such a case, use ```install.sh``` script to compile BWISE on your system; see below.

### Installing BWISE using provided third-party tools

In case above test is ok, then you can proceed as follows to compile and prepare BWISE on your system:


```bash
cd <BWISE-home>
./install.sh
```

### Installing BWISE by compiling all tools

In case above test fails, then you can proceed as follows to compile and prepare BWISE on your system:


```bash
cd <BWISE-home>
./install-full.sh -t <cores>

# adjust <cores> to match your system
```

This installation process may take some time since you are going to compile 5 softwares, including BWISE.

### Installing BWISE as a Docker container

If none of the above mentioned ```install``` solutions work on your system, then you can setup a Docker container.

Please, read [this documentation](docker/README.md).

## Testing BWISE

As soon as BWISE is installed, you can test your installation as follows:

```bash
cd data
./test.sh
```

## Using BWISE with your data

BWISE command-line is as follows:

```bash
./bwise -x examplePairedReads.fa -o workingFolder
```

Options and default values:

-x paired read file (at most one at present, with the reads interleaved)

-u unpaired read file (at most one at present)

-o working folder (Bwise will run the complete pipeline in this folder; default is .)

-s kmer solidity threshold (only kmers occurring at least s times are included in the initial de Bruijn graph; default is 2, which seems a good value when starting from ~100X data, but if the read coverage is very high this can be raised to 5 or even 10)

-S unitig solidity threshold (only unitigs on which at least S reads map are considered valid and retained; default is 2)

-k maximal kmer size (for de Bruijn graph construction; default is 240)

-p superReads cleaning threshold (only super-reads that appear more than p times are retained for the final super-read assembl stepy; default is 2)

-c number of correction steps (default is at most 3)

-t maximum number of threads 

 
## License

BWISE is free software; you can redistribute it and/or modify it under the [Affero GPL v3 license](http://www.gnu.org/licenses/agpl-3.0.en.html).