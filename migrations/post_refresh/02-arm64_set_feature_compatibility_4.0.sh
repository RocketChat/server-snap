#!/bin/bash

source $SNAP/helpers/mongo.sh

start() {
    is_mongod_running || start_mongod
	if ! is_mongod_ready; then
		error "failed to start mongod to set feature compatibility to 4.0"
		return 1
	fi
	if ! is_mongod_primary; then
		error "timed out waiting for mongod instance to become primary"
		return 1
	fi
	set_feature_compatibility "4.0"
	stop_mongod
}
