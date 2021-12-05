#!/bin/bash

source $SNAP/helpers/mongo.sh

start() {
    # In case if the mongo update failed
    # and mongod is unable to start up post refresh
    # this should fail and revert to the local previous
    # revision, avoiding bricking their installs.
    start_mongod && is_mongo_ready && stop_mongod
}
