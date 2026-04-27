#!/bin/bash

source "$SNAP/helpers/mongo.sh"

if is_mongod_running; then
	mongo_eval 'db.version()'
else
	mongod --version | awk '/db version/ {print $3}' | sed 's/v//'
fi
