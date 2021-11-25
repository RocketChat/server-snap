#!/bin/bash

source $SNAP/migrations/lib/mongo_feature_compatibility.sh

start() {
    local v=$(mongo_version_excluding_patch)
    is_feature_compatibility $v || set_feature_compatibility $v
}
