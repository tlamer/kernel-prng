Analysis of randomness levels in the kernel entropy pool after boot
===================================================================

The idea behind this work is to examine the entropy levels in internel linux
kernel entropy pools after boot on machines with constrained hardware such as
embedded devices or virtual machines.

Work already done
-----------------

I've made changes to linux kernel to be able to gather the input of linux prng
and built the Fedora kernel package.

As target machines I've decided to use virtual machines provisioned in openstack
instance. To use them I've prepared a minimal Fedora distribution image with
modified kernel and set of scripts that uploaded the gathered date to control
node. The kernel source code I've used was a stock Fedora kernel with my
patches.

The control node was another openstack Fedora instance that used a set of scripts
to boot new instances of tested image, wait until those instances upload the
data and terminate them.

The repository also includes few scripts I've used to do preliminary data
analysis.

Results so far
--------------

There are several functions in the kernel that pass the entropy to internal
kernel pool. My researched showed that only few of them  provided seemingly
random data while others passed predictable data based on the hardware used. See
more in [docs](https://github.com/tlamer/kernel-prng/tree/master/docs).

Plans
-----

Continue with analysis of the data. Compute Shannon and min entropy from gathered
data. Use other statistical methods to verify the randomness of the data.
