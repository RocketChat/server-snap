#!/bin/bash

source $SNAP/migrations/lib/helpers.sh

mongo() {
    command mongo --quiet --eval "$1"
}

mongo_version_excluding_patch() {
    mongo 'db.version().split(".").slice(0, 2).join(".")'
}

start_mongod() {
  mongod \
    --config=$SNAP_DATA/mongod.conf
    --fork --syslog \
    \
    \
    || error "mongo server start failed"
}

stop_mongod() {
  mongod --dbpath=$SNAP_COMMON --shutdown || error "mongo server shutdown failed"
}

mongo_with_error_check() {
  # 1: command 2: errormsg
  local output=$(mongo "$1")
  (( $(jq -r .ok <<< $output 2>/dev/null || echo 0) == 1 )) && return
  jq -r .errmsg <<< $output >&2 2>/dev/null || echo $output >&2
  error ${2?-"$1" command failed}
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
