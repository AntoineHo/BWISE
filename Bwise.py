#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import time
import shlex, subprocess
import struct
import shutil
import os.path
import tempfile
import argparse
import threading
import multiprocessing
# from random import randint
from operator import itemgetter
from subprocess import Popen, PIPE, STDOUT

# ***************************************************************************
#
#                              Bwise:
#                High order De Bruijn graph assembler
#
#
#
# ***************************************************************************

# ############################################################################
#                                   Utils functions
# ############################################################################

# get the platform
def getPlatform():
    if sys.platform == "linux" or sys.platform == "linux2":
        return "linux"
    elif sys.platform == "darwin":
        return "OSX"
    else:
        print("[ERROR] BWISE is not compatible with Windows.")
        sys.exit(1);


# get the timestamp as string
def getTimestamp():
    return "[" + time.strftime("%H:%M:%S") + " " + time.strftime("%d/%m/%Y") + "] "



# check if reads files are present
def checkReadFiles(readfiles):
    if readfiles is None:
        return True
    allFilesAreOK = True
    #~ for file in readfiles:
    if not os.path.isfile(readfiles):
        print("[ERROR] File \""+file+"\" does not exist.")
        allFilesAreOK = False
    if not allFilesAreOK:
        dieToFatalError("One or more read files do not exist.")


# check if files written by BWISE are present
def checkWrittenFiles(files):
    allFilesAreOK = True
    if not os.path.isfile(files):
        print("[ERROR] There was a problem writing \"" + files + "\".")
        allFilesAreOK = False
    if not allFilesAreOK:
        dieToFatalError("One or more files could not be written.")



# to return if an error makes the run impossible
def dieToFatalError (msg):
  print("[FATAL ERROR] " + msg)
  print("Try `Bwise --help` for more information")
  sys.exit(1);


# launch subprocess
def subprocessLauncher(cmd, argstdout=None, argstderr=None,  argstdin=None):
    args = shlex.split(cmd)
    p = subprocess.Popen(args, stdin = argstdin, stdout = argstdout, stderr = argstderr).communicate()
    return p

def printTime(msg, seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return msg + " %d:%02d:%02d" % (h, m, s)


def printWarningMsg(msg):
    print("[Warning] " + msg)


# ############################################################################
#                                   Correction fonction using Bloocoo
# ############################################################################

def correctionReads(BWISE_MAIN, BWISE_INSTDIR, paired_readfiles, single_readfiles, toolsArgs, fileCase, nb_correction_steps, OUT_DIR, nb_cores):
    try:
        print("\n" + getTimestamp() + "--> Starting Read Correction with Bloocoo...")
        slowParameter = " -slow "
        kmerSizeCorrection = ["31", "63", "95", "127"]
        bloocooversion = ["32", "64", "128", "128"]
        logFile = open( OUT_DIR + "/logs", 'w')
        # os.chdir(BWISE_MAIN)
        os.chdir(OUT_DIR)
        indiceCorrection = 0
        for indiceCorrection in range(min(nb_correction_steps, len(kmerSizeCorrection))):
            # print("       Correction step " + str(indiceCorrection + 1) + "... ", end='', flush=True)
            logHistoCorr = "histocorr" + str(kmerSizeCorrection[indiceCorrection])
            logHistoCorrToWrite = open(logHistoCorr, 'w')
            # Bloocoo
            cmd=BWISE_INSTDIR + "/Bloocoo" + bloocooversion[indiceCorrection] + " -file " + toolsArgs['bloocoo'][fileCase] + slowParameter + "-kmer-size " + kmerSizeCorrection[indiceCorrection] + " -nbits-bloom 24  -out reads_corrected" + str(indiceCorrection + 1) + ".fa -nb-cores " + nb_cores + " -abundance-max 1000"
            print("\tCorrection step " + str(indiceCorrection + 1), flush=True)
            print( "\t\t"+cmd)
            p = subprocessLauncher(cmd, logFile, logFile)
            # Deal with files after Bloocoo

            #TODO=put back the histogram creation
            # cmd=BWISE_INSTDIR + "/h5dump -y -d histogram_"+kmerSizeCorrection[indiceCorrection]+" reads_corrected" + str(indiceCorrection + 1) + ".fa.h5"
            # print("\t\t"+cmd)
            # p = subprocessLauncher(cmd, logHistoCorrToWrite, logHistoCorrToWrite)
            checkWrittenFiles(OUT_DIR + "/reads_corrected" + str(indiceCorrection + 1) + ".fa.h5")
            # if (indiceCorrection > 0):
            #     cmd="rm -f " + OUT_DIR + "/reads_corrected" + str(indiceCorrection) + "* "
            #     print("\t\t\t"+cmd)
            #     p = subprocessLauncher(cmd, None, logHistoCorrToWrite)
            if fileCase == 3:
                cmd="mv reads_corrected" + str(indiceCorrection + 1) + "_0_.fasta reads_corrected" + str(indiceCorrection + 1) + "1.fa "
                print("\t\t\t"+cmd)
                p = subprocessLauncher(cmd)
                p = subprocessLauncher("mv reads_corrected" + str(indiceCorrection + 1) + "_1_.fasta reads_corrected" + str(indiceCorrection + 1) + "2.fa ")
                checkWrittenFiles(OUT_DIR + "/reads_corrected" + str(indiceCorrection + 1) + "1.fa")
                checkWrittenFiles(OUT_DIR + "/reads_corrected" + str(indiceCorrection + 1) + "2.fa")
                toolsArgs['bloocoo'][fileCase] = OUT_DIR + "/reads_corrected" + str(indiceCorrection + 1) + "1.fa," + OUT_DIR + "/reads_corrected" + str(indiceCorrection + 1) + "2.fa"
            else:
                checkWrittenFiles(OUT_DIR + "/reads_corrected" + str(indiceCorrection + 1) + ".fa")
                toolsArgs['bloocoo'][fileCase] = OUT_DIR + "/reads_corrected" + str(indiceCorrection + 1) + ".fa "
            logHistoCorrToWrite.close()
            checkWrittenFiles(OUT_DIR + "/histocorr" + str(kmerSizeCorrection[indiceCorrection]))

        os.chdir(BWISE_MAIN)
        # links and file check
        if nb_correction_steps == 0:
            if fileCase == 3:
                # no correction : linking raw read files to reads_corrected1.fa and reads_corrected2.fa
                cmd="ln -fs " + paired_readfiles + " " + OUT_DIR + "/reads_corrected1.fa"
                print("\t\t\t"+cmd)
                p = subprocessLauncher(cmd, None, subprocess.DEVNULL)
                cmd="ln -fs " + single_readfiles + " " + OUT_DIR + "/reads_corrected2.fa"
                print("\t\t\t"+cmd)
                p = subprocessLauncher(cmd, None, subprocess.DEVNULL)
                checkWrittenFiles(OUT_DIR + "/reads_corrected1.fa")
                checkWrittenFiles(OUT_DIR + "/reads_corrected2.fa")
            else:
                cmd="ln -fs " + toolsArgs['bloocoo'][fileCase] + " " + OUT_DIR + "/reads_corrected.fa"
                print("\t\t\t"+cmd)
                p = subprocessLauncher(cmd, None, subprocess.DEVNULL)
                checkWrittenFiles(OUT_DIR + "/reads_corrected.fa")
        else:
            if fileCase == 3:
                # linking last corrected reads files to reads_corrected1.fa and reads_corrected2.fa
                cmd="ln -fs " + OUT_DIR + "/reads_corrected" + str(indiceCorrection + 1) + "1.fa " + OUT_DIR + "/reads_corrected1.fa"
                print("\t\t\t"+cmd)
                p = subprocessLauncher(cmd, None, subprocess.DEVNULL)
                cmd="ln -fs " + OUT_DIR + "/reads_corrected" + str(indiceCorrection + 1) + "2.fa " + OUT_DIR + "/reads_corrected2.fa"
                print("\t\t\t"+cmd)
                p = subprocessLauncher(cmd, None, subprocess.DEVNULL)
                checkWrittenFiles(OUT_DIR + "/reads_corrected1.fa")
                checkWrittenFiles(OUT_DIR + "/reads_corrected2.fa")
            else:
                cmd="ln -fs " + toolsArgs['bloocoo'][fileCase] + " " + OUT_DIR + "/reads_corrected.fa"
                print("\t\t\t"+cmd)
                p = subprocessLauncher(cmd)
                checkWrittenFiles(OUT_DIR + "/reads_corrected.fa")

        print("\n" + getTimestamp() + "--> Correction Done")
        cmd="rm -f "+ OUT_DIR + "/reads_corrected*.h5"
        print("\t\t"+cmd)
        p = subprocessLauncher(cmd, None, subprocess.DEVNULL)
    except SystemExit:  # happens when checkWrittenFiles() returns an error
        sys.exit(1);
    except KeyboardInterrupt:
        sys.exit(1);
    except:
        print("Unexpected error during read correction:", sys.exc_info()[0])
        dieToFatalError('')




# ############################################################################
#              graph generation with BCALM + kMILL + BGREAT
# ############################################################################

def graphConstruction(BWISE_MAIN, BWISE_INSTDIR, OUT_DIR, fileBcalm, k_max, solidity, unitigFilter, superReadsCleaning, toolsArgs, fileCase, nb_cores, max_tip, min_conflict_overlap,dontcrush):
    try:
        print("\n" + getTimestamp() + "--> Starting Graph construction and Super Reads generation...")
        logs = open(OUT_DIR+"/logs", 'w')
        # os.chdir(BWISE_MAIN)
        os.chdir(OUT_DIR)
        # indiceGraph = 1
        # kmerSize = kmerSize
        coreUsed = "20" if nb_cores == "0" else nb_cores

        kmerSize = "51"
        print("\t#Graph Construction first stage... ", flush=True)
            #  Graph construction, Bcalm
        cmd=BWISE_INSTDIR + "/bcalm -in " + OUT_DIR + "/" + fileBcalm + " -kmer-size " + kmerSize + " -abundance-min " + str(solidity) + " -out " + OUT_DIR + "/out " + " -nb-cores " + nb_cores
        print( "\t\t"+cmd)
        p = subprocessLauncher(cmd, logs, logs)
        checkWrittenFiles(OUT_DIR + "/out.unitigs.fa")
            #  Graph Cleaning
        print("\t\t #Cleaning... ", flush=True)

        # kMILL + tip cleaning
        cmd=BWISE_INSTDIR + "/kMILL out.unitigs.fa " + str(int(kmerSize) - 1) + " " + str(int(kmerSize) - 2)
        print("\t\t\t"+cmd)
        p = subprocessLauncher(cmd, logs, logs)
        checkWrittenFiles(OUT_DIR + "/out_out.unitigs.fa.fa")
        cmd=BWISE_INSTDIR + "/tipCleaner out_out.unitigs.fa.fa "     + str(int(kmerSize) - 1) + " " + str(50+int(kmerSize))
        print("\t\t\t"+cmd)
        p = subprocessLauncher(cmd, logs, logs)
        checkWrittenFiles(OUT_DIR + "/tiped.fa")
        cmd=BWISE_INSTDIR + "/kMILL tiped.fa " + str(int(kmerSize) - 1) + " " + str(int(kmerSize) - 2)
        print("\t\t\t"+cmd)
        p = subprocessLauncher(cmd, logs, logs)
        checkWrittenFiles(OUT_DIR + "/out_tiped.fa.fa")
        cmd="mv out_tiped.fa.fa dbg" + str(kmerSize) + ".fa"
        print("\t\t\t"+cmd)
        p = subprocessLauncher(cmd)
        checkWrittenFiles(OUT_DIR + "/dbg" + str(kmerSize) + ".fa")

        # Read Mapping
        print("\t#Read mapping with BGREAT... ")
        # BGREAT
        cmd=BWISE_INSTDIR + "/bgreat  -k " + kmerSize + " -i 10 " + toolsArgs['bgreat'][fileCase] + " -g dbg" + str(kmerSize) + ".fa -t " + coreUsed + " -a 63 -m 0 -e 100"
        print("\t\t"+cmd)
        p = subprocessLauncher(cmd, logs, logs)
        checkWrittenFiles(OUT_DIR + "/paths")

        cmd=BWISE_INSTDIR + "/numbersFilter paths " + str(unitigFilter) + " cleanedPaths_"+str(kmerSize)+" "+ str(superReadsCleaning) + " dbg" + str(kmerSize) + ".fa " + kmerSize
        print("\t\t"+cmd)
        p = subprocessLauncher(cmd, logs, logs)

        print("\t#Maximal read graph creation and simplification with K2000...")
        cmd=BWISE_INSTDIR +"/run_K2000.sh -i cleanedPaths_"+str(kmerSize)+" -u dbg" + str(kmerSize) + ".fa -k "+kmerSize+" -g compacted_unitigs_k"+kmerSize+".gfa   -f compacted_unitigs_k"+kmerSize+".fa -t "+max_tip+" -c  "+min_conflict_overlap
        print("\t\t"+cmd)
        p = subprocessLauncher(cmd, logs, logs)

        fileBcalm = "compacted_unitigs_k"+kmerSize+".fa";

        kmerSize="201"
        #if False: 

        print("\t#Graph Construction using k= "+str(kmerSize), flush=True)
        
        cmd=BWISE_INSTDIR + "/bcalm -in " + OUT_DIR + "/" + fileBcalm + " -kmer-size " + kmerSize + " -abundance-min 1 -out " + OUT_DIR + "/out2 " + " -nb-cores " + nb_cores
        print( "\t\t"+cmd)
        p = subprocessLauncher(cmd, logs, logs)
        checkWrittenFiles(OUT_DIR + "/out2.unitigs.fa")
              #        Graph Cleaning
        print("\t\t #Cleaning... ", flush=True)
        
        # kMILL + tip cleaning
        cmd=BWISE_INSTDIR + "/kMILL out2.unitigs.fa " + str(int(kmerSize) - 1) + " " + str(int(kmerSize) - 2)
        print("\t\t\t"+cmd)
        p = subprocessLauncher(cmd, logs, logs)
        checkWrittenFiles(OUT_DIR + "/out_out2.unitigs.fa.fa")
        cmd=BWISE_INSTDIR + "/tipCleaner out_out2.unitigs.fa.fa "           + str(int(kmerSize) - 1) + " " + str(50+int(kmerSize))
        print("\t\t\t"+cmd)
        p = subprocessLauncher(cmd, logs, logs)
        checkWrittenFiles(OUT_DIR + "/tiped.fa")
        cmd=BWISE_INSTDIR + "/kMILL tiped.fa " + str(int(kmerSize) - 1) + " " + str(int(kmerSize) - 2)
        print("\t\t\t"+cmd)
        p = subprocessLauncher(cmd, logs, logs)
        checkWrittenFiles(OUT_DIR + "/out_tiped.fa.fa")
        cmd="mv out_tiped.fa.fa dbg_2_" + str(kmerSize) + ".fa"
        print("\t\t\t"+cmd)
        p = subprocessLauncher(cmd)
        checkWrittenFiles(OUT_DIR + "/dbg_2_" + str(kmerSize) + ".fa")
        
        # Read Mapping
        print("\t#Read mapping with BGREAT... ")
        # BGREAT
        cmd=BWISE_INSTDIR + "/bgreat -M -k " + kmerSize + " -i 10 " + toolsArgs['bgreat'][fileCase] + " -g dbg_2_" + str(kmerSize) + ".fa -t " + coreUsed + " -a 63 -m 0 -e 100"
        print("\t\t"+cmd)
        p = subprocessLauncher(cmd, logs, logs)
        checkWrittenFiles(OUT_DIR + "/paths")
        
        cmd=BWISE_INSTDIR + "/numbersFilter paths " + str(unitigFilter) + " cleanedPaths_"+str(kmerSize)+" "+ str(superReadsCleaning) + " dbg_2_" + str(kmerSize) + ".fa "        + kmerSize
#               cmd=BWISE_INSTDIR + "/numbersFilter paths " + 0 + " cleanedPaths_"+str(kmerSize)+" "+ 0 + " dbg" + str(kmerSize) + ".fa " + kmerSize 0 # A tester.
        print("\t\t"+cmd)
        p = subprocessLauncher(cmd, logs, logs)
        # if (True):#if (indiceGraph >1):
              # if int(kmerSize) <= k_max:
        
        # Read Mapping
        print("\t#Maximal read graph creation and simplification with K2000... ")
        crush_buble_option=""
        # print ("crush="+crush)
        if dontcrush:
            crush_buble_option=""
        else:
            crush_buble_option=" -b "
        cmd=BWISE_INSTDIR +"/run_K2000.sh -i cleanedPaths_"+str(kmerSize)+" -u dbg_2_" + str(kmerSize) + ".fa -k "+kmerSize+" -g compacted_unitigs_k"+kmerSize+".gfa -f compacted_unitigs_k"+kmerSize+".fa -t "+max_tip+" -c  "+min_conflict_overlap+crush_buble_option
        print("\t\t"+cmd)
        p = subprocessLauncher(cmd, logs, logs)

        
        
        
        
        
        
        
        
        
        os.chdir(BWISE_MAIN)

        print(getTimestamp() + "--> Done!")
    except SystemExit:  # happens when checkWrittenFiles() returns an error
        sys.exit(1);
    except KeyboardInterrupt:
        sys.exit(1);
    except:
        print("Unexpected error during graph construction:", sys.exc_info()[0])
        dieToFatalError('')





# ############################################################################
#                                   Main
# ############################################################################
def main():

    wholeT = time.time()
    print("\n*** This is BWISE - High order De Bruijn graph assembler ***\n")
    BWISE_MAIN = os.path.dirname(os.path.realpath(__file__))
    BWISE_INSTDIR =  BWISE_MAIN + "/bin"  # todo : change using getPlatform()
    print("Binaries are in: " + BWISE_INSTDIR)

    # ========================================================================
    #                        Manage command line arguments
    # ========================================================================
    parser = argparse.ArgumentParser(description='Bwise - High order De Bruijn graph assembler ')

    # ------------------------------------------------------------------------
    #                            Define allowed options
    # ------------------------------------------------------------------------
    parser.add_argument("-x", action="store", dest="paired_readfiles",      type=str,                   help="input fasta or (compressed .gz if -c option is != 0) paired-end read files. Several read files must be concatenated.")
    parser.add_argument("-u", action="store", dest="single_readfiles",      type=str,                   help="input fasta or (compressed .gz if -c option is != 0) single-end read files. Several read files must be concatenated.")
    parser.add_argument('-s', action="store", dest="min_cov",               type=int,   default = 2,    help="an integer, k-mers present strictly less than this number of times in the dataset will be discarded (default 2)")
    parser.add_argument('-S', action="store", dest="min_cov_uni",                       default = 2,    help="an integer, unitigs present strictly less than this number of times in the dataset will be discarded (default 2)")
    
    parser.add_argument("--min_conflict_overlap", type=str, dest='min_conflict_overlap',
                        help="Minimal conflict overlap. \n\t With M=0: K2000 is exact. \n\t With C>0: K2000 becomes greedy, in this case if a path A could be extended either by B or C and B and C are not collinear, then if the size of the overlap (A,B)>C and the size of the overlap (A,C)<C, then compact A-B but not A-C. If both overlaps are bigger than C or both smaller than C, no compaction is made. \n Note that with C>0, size of unitigs has to be computable, thus K2000 needs to know the k value and the unitig length. Thus, with C>0, options -k and --unitig_file  are mandatory. [DEFAULT 0]", default=0)
    
    parser.add_argument("--max_tip", type=str, dest='max_tip',
                        help=" Dead end smaller or equal than this value are removed from the path graph.\n Note that with C>0, size of unitigs has to be computable, thus K2000 needs to know the k value and the unitig length. Thus, with C>0, options -k and --unitig_file  are mandatory. [DEFAULT 0]", default=0)
    parser.add_argument('--crush_bubbles', action="store_false", dest="crush", help=" Crush the bubbles in the last MSR graph. WARNING - alpha testers only - [DEFAULT False]")
    
    parser.add_argument('-o', action="store", dest="out_dir",               type=str,   default=".",    help="path to store the results (default = .)")
    parser.add_argument('-k', action="store", dest="k_max",                 type=int,   default = 301,  help="an integer, largest k-mer size (default=301)")
    parser.add_argument('-p', action="store", dest="min_cov_SR",            type=int,   default = 2,    help="an integer,  super-reads present strictly less than this number of times will be discarded(default 2)")
    parser.add_argument('-c', action="store", dest="nb_correction_steps",   type=int,   default = 4,    help="an integer, number of steps of read correction (default max=4)")
    parser.add_argument('-t', action="store", dest="nb_cores",              type=str,   default = "0",  help="number of cores used (default max)")
    parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')


    # ------------------------------------------------------------------------
    #               Parse and interpret command line arguments
    # ------------------------------------------------------------------------
    options = parser.parse_args()

    # ------------------------------------------------------------------------
    #                 Print command line
    # ------------------------------------------------------------------------
    print("The command line was: " + ' '.join(sys.argv))


    # ------------------------------------------------------------------------
    #                 Misc parameters
    # ------------------------------------------------------------------------
    k_max               = options.k_max
    min_cov             = options.min_cov
    min_cov_uni         = options.min_cov_uni
    min_cov_SR          = options.min_cov_SR
    nb_correction_steps = options.nb_correction_steps
    nb_cores            = options.nb_cores
    dontcrush               = options.crush
    max_tip             = options.max_tip
    min_conflict_overlap= options.min_conflict_overlap
    

    if nb_correction_steps > 4:
        dieToFatalError("Please use value <= 4 for correction steps.")

    # ------------------------------------------------------------------------
    #               Create output dir and log files
    # ------------------------------------------------------------------------
    OUT_DIR = options.out_dir
    try:
        if not os.path.exists(OUT_DIR):
            os.mkdir(OUT_DIR)
        else:
            printWarningMsg(OUT_DIR + " directory already exists, BWISE will use it.")

        outName = OUT_DIR.split("/")[-1]
        OUT_DIR = os.path.dirname(os.path.realpath(OUT_DIR)) + "/" + outName
        parametersLog = open(OUT_DIR + "/ParametersUsed.txt", 'w');
        parametersLog.write("k_max:%s k-mer_solidity:%s unitig_solidity:%s SR_cleaning:%s correction_steps:%s" %(k_max, min_cov, min_cov_uni, min_cov_SR, nb_correction_steps))
        print("Results will be stored in: ", OUT_DIR)
    except:
        print("Could not write in out directory :", sys.exc_info()[0])
        dieToFatalError('')

    # ------------------------------------------------------------------------
    #                 Parse input read options
    # ------------------------------------------------------------------------
    try:
        bankBcalm = open(OUT_DIR + "/bankBcalm.txt", 'w');
    except:
        print("Could not write in out directory :", sys.exc_info()[0])

    # check if the given paired-end read files indeed exist
    paired_readfiles = None
    single_readfiles = None
    errorReadFile = 0
    if options.paired_readfiles:
        paired_readfiles =  ''.join(options.paired_readfiles)
        try:
            paired_readfiles = os.path.abspath(paired_readfiles)
            checkReadFiles(options.paired_readfiles)
        except:
            paired_readfiles = None
            errorReadFile = 1
    else:
        paired_readfiles = None
        errorReadFile = 1

    # check if the given single-end read files indeed exist
    if options.single_readfiles:
        single_readfiles = ''.join(options.single_readfiles)
        try:
            single_readfiles = os.path.abspath(single_readfiles)
            checkReadFiles(options.single_readfiles)
            errorReadFile *= 0
        except:
            single_readfiles = None
            errorReadFile *= 1
    else:
        single_readfiles = None
        errorReadFile *= 1

    if errorReadFile:
        parser.print_usage()
        dieToFatalError("BWISE requires at least a read file")

    bloocooArg = ""
    bgreatArg = ""
    paired = '' if paired_readfiles is None else str(paired_readfiles)
    single = '' if single_readfiles is None else str(single_readfiles)
    both = paired + "," + single
    toolsArgs = {'bloocoo':{1: paired + " " , 2:  single + " " , 3: both + " "}, 'bgreat':{1:" -x reads_corrected.fa ", 2: " -u reads_corrected.fa ", 3: " -x reads_corrected1.fa  -u reads_corrected2.fa "}}




    if single_readfiles is not None and paired_readfiles is not None:  # paired end + single end
        fileCase = 3
        bankBcalm.write(OUT_DIR + "/reads_corrected1.fa\n" + OUT_DIR + "/reads_corrected2.fa\n")
    elif single_readfiles is None:  # paired end only
        fileCase = 1
        bankBcalm.write(OUT_DIR + "/reads_corrected.fa\n")
    else:  # single end only
        fileCase = 2
        bankBcalm.write(OUT_DIR + "/reads_corrected.fa\n")
    # bankBcalm.write(OUT_DIR + "lost_unitig.fa")
    bankBcalm.close()

    # ========================================================================
    #                                   RUN
    # ========================================================================


    # ------------------------------------------------------------------------
    #                          Correction
    # ------------------------------------------------------------------------
    t = time.time()
    correctionReads(BWISE_MAIN, BWISE_INSTDIR, paired_readfiles, single_readfiles, toolsArgs, fileCase, nb_correction_steps, OUT_DIR, nb_cores)
    print(printTime("Correction took: ", time.time() - t))


    # ------------------------------------------------------------------------
    #                          Graph construction and cleaning
    # ------------------------------------------------------------------------
    t = time.time()
    valuesGraph = graphConstruction(BWISE_MAIN, BWISE_INSTDIR, OUT_DIR, "bankBcalm.txt", k_max, min_cov, min_cov_uni, min_cov_SR, toolsArgs, fileCase, nb_cores,max_tip, min_conflict_overlap,dontcrush)
    print(printTime("Graph Construction took: ", time.time() - t))

    
    

    print(printTime("BWISE assembly took: ", time.time() - wholeT))
    print("Final assembly files are "+OUT_DIR+"/[crushed_]compacted_unitigs_k*.fa and "+OUT_DIR+"/[crushed_]compacted_unitigs_k*.gfa")
    print("Contact information: bwise@inria.fr")



if __name__ == '__main__':
    main()
