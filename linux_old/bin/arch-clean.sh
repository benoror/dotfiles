#!/bin/bash
# Remove old packages from cache
sudo pacman -Sc 
#Remove Orphans
sudo pacman -Rns $(sudo pacman -Qdt | awk '{print $1}')
# Optimize
sudo pacman-optimize && sudo sync
