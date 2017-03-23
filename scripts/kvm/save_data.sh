#!/usr/bin/env bash

main() {
    tmpdir="$(mktemp -d)/$(date '+%F-%H%M%S')"
    datadir="/home/thesis/nfs/data/lnv/$(date +%F)"
    mkdir -p "$tmpdir"

    cp /proc/prng_* "$tmpdir"
    dmesg > "$tmpdir"/dmesg
    if [[ ! -e "$datadir" ]] ; then
        mkdir "$datadir"
    fi

    chown -R thesis:users "${tmpdir}"
    chown -R thesis:users "${datadir}"

    cp -a "$tmpdir" "$datadir"
}

main
