#!/bin/bash

SWITCH="/tmp/showdesktop_ON"

if [ -a "$SWITCH" ]; then

wmctrl -k off && rm /tmp/showdesktop_ON

else

wmctrl -k on && touch /tmp/showdesktop_ON

fi
