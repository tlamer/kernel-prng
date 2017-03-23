#!/usr/bin/env bash

# This is a scrept that sleeps until the star of next minute mod $PERIOD.

[[ ! "$#" -eq 1 ]] && >&2 echo "Specify period. (One positional argument, integer)" && exit 1

PERIOD="$1"

MIN="$(date +%M)"
SEC="$(date +%S)"

DELAY="$((($PERIOD - (10#$MIN % $PERIOD)) * 60 - 10#$SEC))"

echo "Sleeping $DELAY seconds."
sleep $DELAY
