## BWISE Docker

### Requirements

[Docker](https://docs.docker.com/engine/installation/) has to be installed on your system. 

### Making BWISE Docker container

You can prepare a Docker container as follows:

```bash
cd <BWISE-home>
cd docker
docker build -f Dockerfile -t bwise_machine .
```

Container creation may take several minutes.

### Using BWISE container

```bash
docker run --rm -i -t \
       -v <LOCAL_PATH>:/tmp/data \
       bwise_machine \
       <BWISE_ARGUMENTS> 
```

where

```
<LOCAL_PATH>: replace with absolute path to a directory on your 
              system hosting sequence data files to process 
              with BWISE
<BWISE_ARGUMENTS>: BWISE command-line arguments
```

Sample use:

```bash
docker run --rm -i -t \
       -v <BWISE-home>/data:/tmp/data \
       bwise_machine \
       -x /tmp/data/examplePairedReads.fa \
       -u /tmp/data/exampleUnpairedReads.fa \
       -o /tmp/data/wkdir \
       -c 2
```

where

```
<BWISE-home>: absolute path to your BWISE installation.
```

