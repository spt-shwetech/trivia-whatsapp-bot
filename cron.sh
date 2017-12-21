#!/bin/sh
if ps -ef | grep -v grep | grep run.py ; then
        exit 0
else
        python3 /{YOUR_PATH}/run.py >> /{YOUR_PATH}/logs/mac.log &
        exit 0
fi