#!/usr/bin/env python3

import sys
import struct
from collections import Counter

if len(sys.argv) < 2:
    sys.exit(1)

for path in sys.argv[1:]:
    try:
        fd = open(path, 'rb')
    except:
        pass

    entries = []
    zeroes = []
    lens = set()

    while True:
        buflen = 0
        buf = b''

        buflenraw = fd.read(8)
        if len(buflenraw) == 0:
            break

        buflen = struct.unpack('q', buflenraw)[0]
        lens.add(buflen)
        entries.append(fd.read(buflen))

    for entry in entries:
        zeroes.append(Counter(list(entry))[0])

    ctr = Counter(entries)

    lenen = len(entries)
    lendif = len(ctr)

#    stat = {
#        path:'',
#        '# of entries':lenen,
#        '# of different entries':lendif,
#        '# of entry / # of diff entries ratio':lenen/lendif,
#        'avg # of 0x00 per entry':sum(zeroes)/len(zeroes),
#        'lengths of entries':lens,
#    }
#
#    for i in stat:
#        print('{}: {}'.format(i, stat[i]))
#    print()

    print('function: {}'.format(path))
    print('# of entries: {}'.format(lenen))
    print('# of entry classes: {}'.format(lendif))
    print('# of classes / # of entries ratio: {}'.format(lendif/lenen))
    if lendif < 25:
        print('# of occurances of each entry class: {}'.format(list(ctr.values())))
    print('avg # of 0x00 per entry: {}'.format(sum(zeroes)/len(zeroes)))
    print('lengths of entries: {}'.format(lens))

    print()
