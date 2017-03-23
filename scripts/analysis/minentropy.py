#!/usr/bin/env python3

import sys
import math
import collections

def minentropy(samples):
    Cmax = collections.Counter(samples).most_common(1)[0][1]
    N = len(samples)
    Pmax = Cmax/N
    Cbound = Cmax + 2.3 * math.sqrt(N*Pmax*(1-Pmax))
    H = - math.log10(Cbound/N)

    print("N =      {}".format(N))
    print("Cmax =   {}".format(Cmax))
    print("Pmax =   {}".format(Pmax))
    print("Cbound = {}".format(Cbound))
    print("H =      {}".format(H))

if __name__ == "__main__":

    if len(sys.argv) < 2:
        # 1st argument - path
        # 2nd arhument - W (number of bits in each sample)
        print("missing path argument")
        sys.exit(1)

    data = [int(x.strip()) for x in open(sys.argv[1]).readlines()]
    minentropy(data)

# vim: ts=4 sts=4 sw=4 et ai
