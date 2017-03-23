#!/usr/bin/env python3
"""Parse data from /proc/prng_*"""

import os
import sys
import re
import argparse
import logging
import signal
import struct

def sigint_handler(sig, frame):
    """SIGINT signal handler"""
    sys.exit(0)

class dataparser():
    """dataparser class"""
    def __init__(self, filepath, options):
        self.filepath = filepath
        self.options = options
        self.logger = logging.getLogger('dataparser')

        if self.options.append:
            self.mode = 'ab'
        else:
            self.mode = 'wb'

        self.data = self.parse()

    def parse(self):
        """method to parse raw data from /proc/prng_*"""
        try:
            fd = open(self.filepath, 'rb')
        except PermissionError as err:
            self.logger.fatal(err)
            sys.exit(err.errno)

        data = {}
        tmp = b''
        while True:
            fname = b''
            buflen = 0
            buf = b''
            while tmp != b'\x00':
                fname += tmp
                tmp = fd.read(1)

            buflenraw = fd.read(self.options.size_t)
            buflen = struct.unpack('q', buflenraw)[0]
            buf = fd.read(buflen)
            if buflen == 0:
                break

            fname = fname.decode('utf-8')
            if fname not in data.keys():
                data.update({fname:b''})
            data[fname] += buflenraw + buf

            tmp = fd.read(1)
            if tmp == b'':
                break
        fd.close()
        return data

    def storeraw(self):
        """method to store parsed data to files"""
        # mkdir
        dirpath = '{}/{}-{}'.format(self.options.destdir,
                                    os.path.basename(self.filepath),
                                    'parsed')
#        self.logger.debug(dirpath)

        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        # write data to files named after function executed
        for name in self.data:
            fd = open("{}/{}".format(dirpath, name), self.mode)
            fd.write(self.data[name])
            fd.close()

#    def parse_timer_randomness(self):
#        """parse data structure frome add_timer_randomness
#        struct {
#            long jiffies;
#            unsigned cycles;
#            unsigned num;
#        } sample;
#        """
#
#    def parse_device_randomnes_time(self):
#        """unsigned long time = random_get_entropy() ^ jiffies;"""
#        timef = [name for name in self.data.keys() if re.match('add_device_randomness_time.*', name)]
#        times = []
#
#        for name in timef:
#            self.logger.debug(name)
#            while True:

def main():
    """main"""
    # parse command line arguments
    signal.signal(signal.SIGINT, sigint_handler)
    parser = argparse.ArgumentParser(description="""Parse data from
                                     /proc/prng_*.  Also reads from stdin.""")
    parser.add_argument('targetdirs', type=str, nargs='+')
    parser.add_argument('-o', '--destdir', metavar='path', default='',
                        type=str, help='path to output directory')
    parser.add_argument('-s', '--size_t', help='size of size_t', type=int,
                        default=8)
    parser.add_argument('-l', '--long', help='size of long', type=int,
                        default=8)
    parser.add_argument('-u', '--unsigned', help='size of unsigned', type=int,
                        default=4)
    parser.add_argument('--log', help='log level', default=logging.WARN)
    parser.add_argument('-a', '--append', action='store_true', default=True)
#    parser.add_argument('-w', '--overwrite', action='store_false', dest="append")
    options = parser.parse_args()

    logging.basicConfig(level=options.log)
    logger = logging.getLogger(__name__)
#    logger.debug(options)

    for directory in options.targetdirs:
        # search for prng_* in target directory
        try:
            targets = [os.path.abspath('{}/{}'.format(directory, x)) \
                       for x in os.listdir(directory) if re.match('prng_nonblocking', x)]
            targets = [x for x in targets if os.path.isfile(x)]
            logger.debug(targets)
        except (FileNotFoundError, NotADirectoryError) as err:
            logger.fatal(err)
            sys.exit(err.errno)

        if targets == []:
            logger.fatal('Could not find any prng_* files in target directory.')
            sys.exit(1)

        # parse the data
        for target in targets:
            datapar = dataparser(target, options)
            datapar.storeraw()

if __name__ == "__main__":
    main()

# vim: ts=4 sts=4 sw=4 et si
