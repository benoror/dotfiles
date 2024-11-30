#!/bin/bash
# Setup wireless
sudo /usr/sbin/iwconfig $1 essid $2 key $3 &&
sudo dhclient $1
