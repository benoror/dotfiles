#!/bin/bash
tail -f /var/log/syslog &
tail -f /var/log/debug &
tail -f /var/log/dmesg
