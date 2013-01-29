#!/bin/bash

find $1 -exec grep -l $2 {} \;
