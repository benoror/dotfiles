#!/bin/bash
sudo /etc/rc.d/wicd stop
sudo ifconfig wlan0 down
sudo macchanger -e wlan0
sudo ifconfig wlan0 up
sudo /etc/rc.d/wicd start
