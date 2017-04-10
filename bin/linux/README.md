== Comment

This folder contains pre-compiled binary of BWISE dependencies for Linux.

These binaries are build on [Inria/Jenkins platform](https://ci.inria.fr/gatb-core/view/BWISE/) using a Fedora 20 system running gcc 4.8.

== Requirements

To use these tools, your Linux system should have to provide you with a libc++ release GLIBCXX_3.4.15 minimum.

To figure out if your Linux is fine, proceeds as follows:

```bash
# Locate libc++ on your system
$ /sbin/ldconfig -p | grep stdc++

# Find supported releases of LIBCXX 
$ strings /usr/lib/libstdc++.so.6  | grep LIBCXX

# Your system is OK if you the above command dumps GLIBCXX_3.4.15
```

== Install procedure
 
The binaries are retrieved and placed here as follows:

curl -O http://gatb-tools.gforge.inria.fr/ci-inria/bwise-bin-dep-linux-gcc48.tgz
tar -zxf bwise-bin-dep-linux-gcc48.tgz
rm bwise-bin-dep-linux-gcc48.tgz

This prodcedure is done by Genscale team only when needed; _i.e._ when there is an update of one of these tools.

