#!/bin/bash
ls -al | grep -v dotfiles | awk '{print }'
