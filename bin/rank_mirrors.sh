#!/bin/bash
sed '/^#\S/ s|#||' /etc/pacman.d/mirrorlist | sed '/^#/d' | rankmirrors -n 6 -
