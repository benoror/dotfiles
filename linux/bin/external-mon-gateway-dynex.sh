#!/bin/sh

xrandr | grep "VGA1 connected 1360" > /dev/null

if [ $? = '0' ]; then
  echo "[VGA1] Off"
  xrandr --output VGA1 --off
else
  echo "[VGA1] On"
  xrandr --output VGA1 --mode 1360x768 --right-of LVDS1
fi
