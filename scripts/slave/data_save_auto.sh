#!/bin/bash

set -x

main (){
    # sanity do not continue if "nodata" is in /proc/cmdline
    grep -qw 'nodata' /proc/cmdline && exit 0 ;

    while true ; do
        dmesg | grep -q 'stopping gathering data for' && {
             /home/fedora/save_data.sh
            sudo poweroff
            break
        }
        sleep 5
    done
}

main

