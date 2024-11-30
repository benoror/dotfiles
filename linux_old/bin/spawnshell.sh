#!/bin/bash
# By:  benoror <benoror@gmail.com>
#
# spawns a remote shell or runs a local shell whether it's on the current machine or not
# $1 = hostname

if [ "$(hostname)" == "$1" ]; then
    bash
else
    echo "Waiting for shell..."
    ssh "$1.local"
    if [ "$?" != 0 ]; then
        read
    fi
fi
