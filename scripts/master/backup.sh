#!/bin/bash

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

main() {
    HOME="/home/fedora"
    DATE="$(date +%F)"

    BCP="${HOME}/bcp"
    SHA="${BCP}/data.sha256"
    DATA="data-${DATE}"
    ARCHIVE="data-${DATE}.tar.xz"

    cd ~/

    [[ -e "$BCP/$ARCHIVE" ]] && { >&2 echo "Archive already exists. Exitting." ; exit 1 ; }
    [[ -e "$HOME/data" ]] || { >&2 echo "$HOME/data was not found. Exitting." ; exit 1 ; }

    echo "Changing dir name."
    mv -vi "${HOME}/data/" "${HOME}/${DATA}" || { >&2 echo "mv failed. Exitting." ; exit 1 ; }
    echo

    echo "Creating xz tar archive."
    tar cvfJ "${BCP}/${ARCHIVE}" "${DATA}" || { >&2 echo "tar failed. Exitting." ; exit 1 ; }
    echo

    echo "Computing sha256sum of new archive."
    sha256sum "${BCP}/${ARCHIVE}" | sed 's;/.*/;;' >> "${SHA}"
    echo

    if ask "Delete the original data? $DATA" Y ; then
        rm -rf "${HOME}/${DATA}"
    fi
    echo

    mkdir -v "$HOME/data" 

    cd - &> /dev/null
}

main

# vim: ts=4 sts=4 sw=4 et si
