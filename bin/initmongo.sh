#! /bin/bash

echo "initializing replset if necessary... in 30 seconds"
sleep 30

echo "after 30 seconds, checking for replset..."
mongo $SNAP/bin/initmongoreplset.js

