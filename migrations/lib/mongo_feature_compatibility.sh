#!/bin/bash

source $SNAP/migrations/lib/mongo.sh

is_feature_compatibility() {
    local v=$(
        mongo_with_error_check_and_capture_output '
            JSON.stringify(db.adminCommand({
                getParameter: 1,
                featureCompatibilityVersion: 1
            }))
        '
    )
    test "$(jq .featureCompatibilityVersion.version -r <<< $v)" == "$1"
}

set_feature_compatibility() {
    mongo_with_error_check "JSON.stringify(db.adminCommand({ setFeatureCompatibilityVersion: \"$1\" }))"
}
