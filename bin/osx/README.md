## Comment

This folder contains pre-compiled binary of BWISE dependencies for OSX.

These binaries are build on [Inria/Jenkins platform](https://ci.inria.fr/gatb-core/view/BWISE/) using a Mavericks (OSX 10.9) system running clang 600.0.51.

## Requirements

To use these tools, your OSX system has to be 10.9+.

## Install procedure
 
The binaries are retrieved and placed here as follows:

```bash
curl -O http://gatb-tools.gforge.inria.fr/ci-inria/bwise-bin-dep-osx-clang6.tgz
tar -zxf bwise-bin-dep-osx-clang6.tgz
rm bwise-bin-dep-osx-clang6.tgz
```

This prodcedure is done by Genscale team only when needed; _i.e._ when there is an update of one of these tools.

