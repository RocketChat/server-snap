#!/bin/bash

source $SNAP/helpers/common.sh

start() {
	if ! has_avx; then
		error "Your cpu does not support avx or avx2 instructions, which is required to run mongo 5.x, shipped with the next version of this snap."
		return 1
	fi
	return 0
}
