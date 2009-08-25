#!/bin/bash

# wget's AUR Tarball and then make PKGBUILD with deps

PKDIR=`wget -O - $1 | tar zxvf - | tail -2 | head -1 | awk 'BEGIN { FS = "/" } ; { print $1 }'`
echo -e "\n\t+Change dir: $PKDIR\n"
pushd $PKDIR &&
makepkg -s
