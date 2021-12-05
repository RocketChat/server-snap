#! /bin/bash

source $SNAP/helpers/caddy.sh

if [[ -s $SNAP_DATA/Caddyfile ]]; then
  # Prioritize caddy v2, if fails, try caddy v1
  start_caddy_v2_with_config || start_caddy_v1_with_config
else
  site_url=$(snapctl get siteurl)
  [[ $site_url =~ ^https:// ]] && caddy_v2_reverse_proxy $site_url http://127.0.0.1:$(snapctl get port)
fi
