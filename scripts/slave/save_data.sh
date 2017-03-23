#!/usr/bin/env bash

main() {
    tmpdir="$(mktemp -d)/$(date '+%F-%H%M%S').${HOSTNAME%%.*}"
    mkdir "$tmpdir"
#    tmpdir="$(mktemp -d "/tmp/$(date '+%F-%H%M%S').$(hostname)")"
    destination="fedora@pkotvan-master.usersys.redhat.com:data"

    cp /proc/prng_* "$tmpdir"
    dmesg > "$tmpdir/dmesg"

    rsync -rq "$tmpdir" "$destination"

    rm -rf "$tmpdir"
}

main
