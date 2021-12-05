#!/bin/bash

source $SNAP/helpers/common.sh
source $SNAP/helpers/environment.sh

caddy() {
    local v=${1?}
    shift
    caddy$v "$@"
}

start_caddy_v1_with_config() {
    caddy 1 -conf=$SNAP_DATA/Caddyfile
}
start_caddy_v2_with_config() {
    caddy 2 run --config=$SNAP_DATA/Caddyfile
}
caddy_v2_reverse_proxy() {
    caddy 2 reverse-proxy --change-host-header \
      --from=${1?} --to=${2?}
}
