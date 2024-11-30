#!/bin/bash

# Tar DIR, gzip it, ssh'm, gunzip'it and untar it

if [ $# -lt 2 ]; then
    echo -e "\n\tUsage: $0 dir user@server\n"
    exit
fi

tar -cvf - $1 | gzip -c | ssh -C $2 "gunzip -c | tar -x"
