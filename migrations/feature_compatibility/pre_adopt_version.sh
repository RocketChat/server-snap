#!/bin/bash

source $SNAP/helpers/mongo.sh

start() {
    local v=$(mongo_version_excluding_patch)
    is_feature_compatibility $v || set_feature_compatibility $v
}
