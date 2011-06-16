#!/bin/sh

# hide mouse cursor when idle
unclutter -idle 5 -noevents &

# set background -- better in awesome startup
#sh .fehbg &

# thunar
# https://wiki.archlinux.org/index.php/Thunar
thunar --daemon &

# volume widget
volwheel &

# wicd
wicd-client &

# Dropbox
(sleep 300 && /usr/bin/dropboxd) &

exec awesome
