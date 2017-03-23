#!/bin/bash

err() {
    echo "$@" 1>&2
}

debug() {
    [[ $DEBUG -eq 1 ]] && "$@" || :
}

function ask {
    while true; do

        if [ "${2:-}" = "Y" ]; then
            prompt="Y/n"
            default=Y
        elif [ "${2:-}" = "N" ]; then
            prompt="y/N"
            default=N
        else
            prompt="y/n"
            default=
        fi

        # Ask the question
        read -p "$1 [$prompt] " REPLY

        # Default?
        if [ -z "$REPLY" ]; then
            REPLY=$default
        fi

        # Check if the reply is valid
        case "$REPLY" in
            Y*|y*) return 0 ;;
            N*|n*) return 1 ;;
        esac

    done
}

kernel_build() {
    # function for kernel installation
    local target="$1"
    local ver="$2"
    local dest="$3"
    local bzimage="$target/arch/x86_64/boot/bzImage"
    local kernel="$dest/kernel-${ver}"
    local kernln="$dest/kernel-last"

    debug echo "target: $target"
    debug echo "ver: $ver"
    debug echo "destination: $dest"
    debug echo "kernel: $kernel"

    # build kernel
    time make -j5
    # copy kernel to destination
    echo "copy the kernel"
    cp -v -f -i "$bzimage" "$kernel"
    [[ $? -ne 0 ]] && { err "could not copy the kernel" ; return 3 ; }
    # create symlink
    [[ -e $kernln ]] && rm -v "$kernln"
    ln -v -r -s "$kernel" "$kernln"
    [[ $? -ne 0 ]] && { err "could not create symlink" ; return 4 ; }
}

main() {
    # check if running as root
    # get target parameter
    if [[ $# -eq 1 ]] ; then
        TARGET="$(readlink -f "$1")"
    else
        err "specify target directory with kernel to build"
        exit 2
    fi

    DEST="$HOME/build"

    # sanity checks
    [[ ! -d $DEST ]] && { err "problem with $DEST directory" ; exit 3 ;}

    if [[ -d $TARGET ]] ; then
        cd "$TARGET"
    else
        err "could not cd to $TARGET"
        exit 1
    fi

    # get version string
    VER="$(make kernelrelease)"
    [[ -z $VER ]] && { err "could not get kernel version string" ; exit 2 ; }

    # kernel install
    kernel_build "$TARGET" "$VER" "$DEST"
}

main "$@"
exit "$?"

