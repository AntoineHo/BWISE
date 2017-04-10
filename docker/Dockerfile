#########################################################################################
#
#  Docker file for BWISE project.
#
#########################################################################################
#
# Docker build command:
#
#    docker build -f Dockerfile -t bwise_machine .
#
# Docker test command:
#
#  After building the container, you can test it as follows. Just update host directory
#  targeting 'BWISE/data' for '-v' argument; however, DO NOT change '/tmp/data'.
#
#    docker run --rm -i -t -v /Users/pdurand/git/BWISE/data:/tmp/data bwise_machine -x /tmp/data/examplePairedReads.fa -u /tmp/data/exampleUnpairedReads.fa  -o /tmp/data/wkdir -c 2
#
# Docker run command.
#
#  You can enter the container using bash, as follows. First, uncomment ENTRYPOINT
#  directive at the end of this Dockerfile. Then re-run a 'docker build' (see above).
#  Finally, use one of these commands:
#
#  - use to enter the machine with bash (maintenance, tests, etc.):
#
#    docker run -i -t bwise_machine bash           <-- keep container state on leave
#
#  - use with caution:
#
#    docker run --rm -i -t bwise_machine bash      <-- DESTROY container on leave
#
#########################################################################################

# ###
#     Base commands
#
#     We use a Debian 8 (Jessie) Linux
#
FROM debian:jessie

# who to blame?
LABEL mainteners="Patrick Durand <patrick.durand@inria.fr>

# ###
#    Configuring gcc and cmake release
#
ENV GCC_VERSION=4.9

# How many jobs to run in parallel ?
ENV NB_CORES="2"

# ###
#     Package installation and configuration
#
#     install latest packages of the base system
#     as well as packages required to compile pyGATB
#
RUN echo "APT::Install-Recommends \"false\";\nAPT::Install-Suggests \"false\";" >> /etc/apt/apt.conf \
    && apt-get update && apt-get -y dist-upgrade \
    && apt-get install -y vim git wget make zlib1g-dev \
    && apt-get clean \
    && git config --global http.sslVerify false

# ###
#     Compiler installation
#
#     We need a c/c++ compiler in an appropriate release.
#     Note: update-alternatives used by cmake installer (./boostrap)
#           to locate gcc
#
RUN apt-get install -y --no-install-recommends \
    gcc-${GCC_VERSION} g++-${GCC_VERSION} gcc-${GCC_VERSION}-base \
    && update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-${GCC_VERSION} 100 \
    && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-${GCC_VERSION} 100 \
    && apt-get clean

# ###
#     Python3 installation
#   
RUN apt-get install -y python3 python3-dev python3-pip \
    && apt-get clean

# ###
#     Build BWISE
#
RUN cd /opt \
    && git clone https://github.com/Malfoy/BWISE.git \
    && cd BWISE \
    && git checkout docker 

RUN cd /opt/BWISE && ./install-dep.sh -t ${NB_CORES} \
    && cd /opt/BWISE/src && make clean

RUN apt-get purge -y gcc-${GCC_VERSION} git wget make && apt-get clean

#RUN cd /opt/BWISE/data && ./test.sh && rm -rf folderTest

# ###
#
# Start BWise
#
#ENTRYPOINT ["/opt/BWISE/bwise"]

