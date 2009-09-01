#!/bin/sh

if [ $1 = 'up' ]; then
    amixer set PCM 2+
elif [ $1 = 'down' ]; then
    amixer set PCM 2-
elif [ $1 = 'mute' ]; then
    amixer set PCM toggle
else
    echo "Unknown control command: $1" >&2
    exit 1
fi
VOLUME=$(amixer sget PCM | sed '/^ *Front\ Left: /{s/^.*\[\(.*\)%\].*/\1/;p;};d;')
STATUS=$(amixer sget PCM | awk '$2 == "Left:" { print $NF; }')
if [ $STATUS = '[off]' ]; then
    ICON=audio-volume-muted
else
    echo $VOLUME
    if [ $VOLUME -eq 0 ]; then
        ICON=audio-volume-off
    elif [ $VOLUME -lt 33 ]; then
        ICON=audio-volume-low
    elif [ $VOLUME -lt 66 ]; then
        ICON=audio-volume-medium
    else
        ICON=audio-volume-high
    fi
    VOLUME="${VOLUME}%"
fi
#notify-send "Volume $VOLUME" -i $ICON -h string:x-canonical-private-synchronous:
