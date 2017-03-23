#!/bin/bash

main (){
    # sanity do not continue if "nodata" is in /proc/cmdline
    grep -qw 'nodata' /proc/cmdline && exit 0 ;

    while true ; do
        dmesg | grep -o 'stopping gathering data for' && {
            ./root/save_data.sh
            poweroff
        }
        sleep 5
    done
}

main

