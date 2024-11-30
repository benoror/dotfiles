#!/bin/bash
reflector | grep -v "#" | awk '{print $3}' | awk 'BEGIN { FS = "/" } ; {print "http://"$3}' | xargs -I _ rankmirrors -n 6 -u _
