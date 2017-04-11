ontinuous integration script for Jenkins            #
#--------------------------------------------------------------#
#
# Default mode :
# This script will exit with error (exit code 1) if any of its steps fails.
# To change this behaviour, choose DO_NOT_STOP_AT_ERROR in Jenkins (see below).
#--------------------------------------------------------------#
set +xv

echo "
-----------------------------------------
 Miscellaneous information 
-----------------------------------------
date      : `date`
hostname  : `hostname`
pwd       : `pwd`

-----------------------------------------
 Jenkins build parameters (user defined)
-----------------------------------------
BRANCH_TO_BUILD      : ${BRANCH_TO_BUILD}
INRIA_FORGE_LOGIN    : ${INRIA_FORGE_LOGIN}
DO_NOT_STOP_AT_ERROR : ${DO_NOT_STOP_AT_ERROR}

-----------------------------------------
 Jenkins build parameters (built in)
-----------------------------------------
BUILD_NUMBER         : ${BUILD_NUMBER}
JOB_NAME             : ${JOB_NAME}

"

# Make sure, we use the appropriate cmake

export PATH=/home/ci-gatb/cmake-3.7.2-Linux-x86_64/bin:$PATH

error_code () { [ "$DO_NOT_STOP_AT_ERROR" = "true" ] && { return 0 ; } }


[ "$DO_NOT_STOP_AT_ERROR" != "true" ] && { set -e ; } || { echo "(!) DEBUG mode, the script will NOT stop..." ; echo; }
set -xv

# quick look at resources
#---------------------------------------------------------------
free -h
#---------------------------------------------------------------
lstopo
#---------------------------------------------------------------
df -kh
#---------------------------------------------------------------


################################################################
#                       COMPILATION                            #
################################################################

gcc --version
g++ --version
cmake --version

# home directory of the task on the Jenkins slave
WK_DIR=/home/ci-gatb/workspace/$JOB_NAME

# where is the source code
GIT_DIR=$WK_DIR/BWISE

# where will be created the binaries
BW_BIN_DIR=$WK_DIR/bin


# we always start with a fresh directory structure
if [ -d $GIT_DIR ]; then
  cd $WK_DIR
  rm -rf BWISE
fi

if [ -d $BW_BIN_DIR ]; then
  cd $WK_DIR
  rm -rf bin
fi

# we clone the git project
cd $WK_DIR
git clone https://github.com/Malfoy/BWISE.git
cd $GIT_DIR
if [ "$BRANCH_TO_BUILD" != "master" ]; then
  git checkout $BRANCH_TO_BUILD
fi

# we compile
./install-full.sh -f $BW_BIN_DIR -t 8

# we make a test
cd data
./test.sh

cd $BW_BIN_DIR

# we get how we make the binaries
INFO_FILE=bwise-dep-linux.txt
objdump --special-syms -Tw Bloocoo32 | grep GLIBC | cut -d ' ' -f 10 | grep GLIBC | sort -u > ${INFO_FILE}
uname -a >> ${INFO_FILE}
gcc --version >> ${INFO_FILE}
cat ${INFO_FILE}

# we package binary dependencies
TAR_BALL=bwise-bin-dep-linux-gcc48.tgz
tar -cvzf $TAR_BALL ${INFO_FILE} Bloocoo* bcalm bgreat kMILL sequencesCleaner tipCleaner

# we upload binary deps to ci-inria
scp $TAR_BALL ${INRIA_FORGE_LOGIN}@scm.gforge.inria.fr:/home/groups/gatb-tools/htdocs/ci-inria

