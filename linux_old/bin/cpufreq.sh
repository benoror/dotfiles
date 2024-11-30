#!/bin/sh
sudo cpufreq-set -c 0 -g $1
sudo cpufreq-set -c 1 -g $1
