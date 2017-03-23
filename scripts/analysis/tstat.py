#!/usr/bin/env python3

import sys
import struct

if len(sys.argv) < 2:
    sys.exit(1)

entries = []

for path in sys.argv[1:]:
    try:
        fd = open(path, 'rb')
    except:
        pass

    lens = set()

    while True:
        buflen = 0
        buf = b''

        buflenraw = fd.read(8)
        if len(buflenraw) == 0:
            break

        buflen = struct.unpack('q', buflenraw)[0]
        lens.add(buflen)

        foo = fd.read(buflen)

        print(int.from_bytes(foo, 'little'))

for entry in entries:
    print(struct.unpack('<q', entry)[0])

