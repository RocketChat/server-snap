#!/bin/bash

source $SNAP/helpers/mongo.sh

start() {
	if !is_mongod_running; then
		start_mongod
	fi
	is_mongod_ready
	is_mongod_primary
	local v="$(mongod_fcv)"
	echo "Expected FCV: $fcv"
	if is_feature_compatibility "$v"; then
		echo "Expected FCV matches current FCV"
		return
	fi
	if set_feature_compatibility "$v"; then
		echo "FCV set to $v"
	else
		echo "Failed to set FCV to $v"
		exit 1
	fi
}
