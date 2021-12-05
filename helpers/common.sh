#!/bin/bash

abort() { exit 1; }

error() {
  printf "[ERROR] %s\n" "$*" >&2
  [[ $(snapctl get ignore-errors) == "true" ]] || abort
}

init_user_environment_variables() {
  # Check both $SNAP_COMMON and $SNAP_DATA
  # I was hoping this to work without a for loop like this
  # find $SNAP_COMMON $SNAP_DATA -maxdepth 1 -regex '.*\.env$' \
  #  | while read filename; do source $filename; done
  set -a
  for filename in $(find $SNAP_COMMON $SNAP_DATA -maxdepth 1 -regex '.*\.env$'); do source $filename; done
  set +a
}
