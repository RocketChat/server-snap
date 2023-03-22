#!/bin/bash

source $SNAP/helpers/common.sh

start() {
	if (($(grep -Ewc 'avx2?' /proc/cpuinfo) == 0)); then
		error "Your cpu does not support avx or avx2 instructions, which is required to run mongo 5.x, shipped with the next version of this snap."
	fi
	return 0
}
