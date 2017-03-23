#!/usr/bin/env python2
"""Monitor slaves for data gathering."""

import os
import sys
import signal
import re
import time
import threading
from requests import ConnectionError
from novaclient import client
from novaclient import exceptions


def debug(msg):
    """Simple print to stderr."""
    print >> sys.stderr, msg
    sys.stderr.flush()


def sig_handler(signum, frame):
    """Signal handler for clean exit on SIGINT."""
    sys.exit(0)


def align_clock(period=3):
    """Synchronize with real time."""
    minutes = int(time.strftime('%M')) % period
    seconds = int(time.strftime('%S'))

    sleep_time = (period - (minutes % period)) * 60 - seconds
    debug("Aligning with clock, sleeping for {} seconds.".format(sleep_time))
    time.sleep(sleep_time)


def nova_init():
    """Acquire credentials from environment variables."""
    creds = {}
    try:
        creds['username'] = os.environ['OS_USERNAME']
        creds['api_key'] = os.environ['OS_PASSWORD']
        creds['auth_url'] = os.environ['OS_AUTH_URL']
        creds['project_id'] = os.environ['OS_TENANT_NAME']
    except KeyError as err:
        debug("Problem with environment variable: {0}. Exitting.".format(err))
        sys.exit(1)

    return client.Client("2", **creds)


def slave_mon(slave):
    """Function monitoring slave activity."""
    state = 0
    mytimer = sleep_timer()

    while True:
        try:
            slave.get()
        # if the slave can not be found return
        except exceptions.NotFound as err:
            print "{}: {} slave not found".format(
                time.strftime('%Y-%m-%d %H:%M:%S'), slave.name)
            sys.stdout.flush()
            return
        except ConnectionError as err:
            print "{}: {} connection error, waiting".format(
                time.strftime('%Y-%m-%d %H:%M:%S'), slave.name)
            state += 1
            mytimer.sleep()
            continue

        # start the slave if shut down
        task_state = getattr(slave, 'OS-EXT-STS:task_state')
        if slave.status == u'SHUTOFF' and task_state is None:
            print "{}: {} started".format(time.strftime('%Y-%m-%d %H:%M:%S'),
                                          slave.name)
            sys.stdout.flush()

            try:
                slave.start()
            except exceptions.Conflict as err:
                print "{}: {} {}".format(time.strftime('%Y-%m-%d %H:%M:%S'),
                                         slave.name, err)
                state += 1
                mytimer.sleep()
                continue
            except ConnectionError as err:
                print "{}: {} connection error, waiting".format(
                    time.strftime('%Y-%m-%d %H:%M:%S'), slave.name)
                state += 1
                mytimer.sleep()
                continue

            state = 0
            mytimer.sleep()
            continue

        elif slave.status == u'MIGRATING' or task_state == u'migrating':
            print "{}: {} migrating".format(time.strftime('%Y-%m-%d %H:%M:%S'),
                                            slave.name)
            mytimer.sleep()
            continue

        # if the slave is still running wait two more periods then force shut down
        else:
            if state > 1 and task_state is None:
                try:
                    slave.stop()
                except exceptions.Conflict as err:
                    print "{}: {} {}".format(
                        time.strftime('%Y-%m-%d %H:%M:%S'), slave.name, err)
                    state += 1
                    mytimer.sleep()
                    continue
                except ConnectionError as err:
                    print "{}: {} connection error, waiting".format(
                        time.strftime('%Y-%m-%d %H:%M:%S'), slave.name)
                    state += 1
                    mytimer.sleep()
                    continue

                state = 0
                print "{}: {} force shut down".format(
                    time.strftime('%Y-%m-%d %H:%M:%S'), slave.name)
                mytimer.sleep()
                continue
            else:
                state += 1
                print "{}: {} slave active, waiting".format(
                    time.strftime('%Y-%m-%d %H:%M:%S'), slave.name)
                mytimer.sleep()
                continue


class sleep_timer(object):
    """Timer synchronized with real time"""

    def __init__(self, period=3):
        self.period = period * 60
        self.last_time = int(time.strftime('%M')) * 60 + int(
            time.strftime('%S'))

    def sleep(self):
        """Sleep aligned with clock."""
        current_time = int(time.strftime('%M')) * 60 + int(time.strftime('%S'))
        sleep_time = (self.last_time + self.period) - current_time
        extend_time = self.period

        while sleep_time < 0:
            sleep_time += self.period
            extend_time += self.period
            debug(
                "{} sleep time ended up negative, extending sleep time".format(
                    time.strftime('%Y-%m-%d %H:%M:%S')))

        time.sleep(sleep_time)

        # modify last_time
        self.last_time = (self.last_time + extend_time) % 3600


def main():
    """Main."""

    # set signal handler
    signal.signal(signal.SIGINT, sig_handler)

    # initialize nova client
    nova = nova_init()

    try:
        slaves = [slave for slave in nova.servers.list()
                  if re.search('pkotvan-slave(-[0-9a-z]+)+', slave.name)]
    except ConnectionError as err:
        print "{}".format(err)
        sys.exit(1)

    threads = []

    # create threads
    for entry in slaves:
        threads.append(threading.Thread(name=entry.name,
                                        target=slave_mon,
                                        args=(entry, )))

    debug(time.strftime('%Y-%m-%d %H:%M:%S'))
    align_clock()

    # start threads
    for thread in threads:
        try:
            thread.start()
        except (KeyboardInterrupt, SystemExit):
            sys.exit()
        time.sleep(15)

    # wait for threads to join
    while threads != []:
        for thread in threads:
            thread.join(20)
            if not thread.is_alive():
                print "{}: {} was joined.".format(
                    time.strftime('%Y-%m-%d %H:%M:%S'), thread.name)
                threads.remove(thread)


if __name__ == "__main__":
    main()

# vim: ts=4 sts=4 sw=4 et ai
