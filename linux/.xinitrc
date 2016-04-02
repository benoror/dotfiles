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

# VMWare copy-paste
vmware-user-suid-wrapper &

#Synergy Client
#synergyc --daemon benja-pc &
#(sleep 30 && qsynergy && sleep 10 && setxkbmap es) &

# Dropbox
(sleep 120 && /usr/bin/dropboxd) &

exec awesome
