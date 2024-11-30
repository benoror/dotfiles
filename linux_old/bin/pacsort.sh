#!/bin/bash
# Sort packages according their size
pacman -Qi | grep -E '^(Name|Installed Size)' | sed ':a;N;$!ba;s/\nI/ I/g' | awk '{print $7 " " $8 " " $3}' | sort -rn
