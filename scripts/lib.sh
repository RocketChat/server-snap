#!/usr/bin/env bash

_escape_regex() {
	echo "$1" | sed -e 's/[]\/$*.^|()[]/\\&/g'
}

get_latest_version_for_channel() {
	local channel="$1"
	test -n "$channel" || {
		echo "Channel is required"
		return 1
	}

	snap info rocketchat-server | awk "/$(_escape_regex "$channel")/ { print \$2 }"
}
