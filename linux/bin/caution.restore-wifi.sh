#!/bin/bash
gksudo rm /var/lib/dhcpcd/dhcpcd-wlan0.lease
gksudo rmmod iwlagn
gksudo modprobe iwlcore rfkill cfg80211 mac80211 iwlagn
gksudo modprobe iwlagn
