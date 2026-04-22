#!/bin/bash

source $SNAP/helpers/mongo.sh

start() {
    local v
    { is_mongod_running || start_mongod; } && is_mongod_ready && v=$(mongod_fcv) && is_mongod_primary && { is_feature_compatibility $v || set_feature_compatibility $v; } && stop_mongod
}
