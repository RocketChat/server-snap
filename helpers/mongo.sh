#! /bin/bash

source $SNAP/helpers/common.sh
source $SNAP/helpers/environment.sh

readonly MAX_MONGOD_START_WAIT_SECONDS=1
readonly MAX_MONGOD_START_RETRY_COUNT=30
readonly MAX_MONGOD_PRIMARY_WAIT_SECONDS=5
readonly MAX_MONGOD_PRIMARY_RETRY_COUNT=10

start_mongod() {
  mongod --config=$SNAP_DATA/mongod.conf --fork --syslog || error "mongo server start failed"
}

stop_mongod() {
  mongod --dbpath=$SNAP_COMMON --shutdown || error "mongo server shutdown failed"
}

mongo() {
  command mongo --quiet --eval "$1"
}

mongo_version_excluding_patch() {
    mongo 'db.version().split(".").slice(0, 2).join(".")'
}

mongo_with_error_check() {
  # 1: command 2: errormsg
  local output=$(mongo "$1")
  (( $(jq -r .ok <<< $output 2>/dev/null || echo 0) == 1 )) && return
  jq -r .errmsg <<< $output >&2 2>/dev/null || echo $output >&2
  error ${2?-"$1" command failed}
}

is_mongo_ready() {
  for _ in $(seq 0 $MAX_MONGOD_START_RETRY_COUNT); do
    (( $(mongo 'db.adminCommand({ ping: 1 }).ok') == 1 )) && return
    sleep $MAX_MONGOD_START_WAIT_SECONDS
  done
  error "mongod server start wait timed out"
}

is_primary() {
  for _ in $(seq 0 $MAX_MONGOD_PRIMARY_RETRY_COUNT); do
    [[ $(mongo 'db.hello().isWritablePrimary') == "true" ]] && return
    sleep $MAX_MONGOD_PRIMARY_WAIT_SECONDS
  done
  error "primary selection wait timed out"
}

mongo_with_error_check_and_capture_output() {
  # 1: command 2: errormsg
  local output=$(mongo "$1")
  (( $(jq -r .ok <<< $output 2>/dev/null || echo 0) == 1 )) && {
      echo $output
      return
  }
  jq -r .errmsg <<< $output >&2 2>/dev/null || echo $output >&2
  error ${2?-"$1" command failed}
}

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
