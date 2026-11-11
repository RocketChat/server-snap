#!/bin/bash

declare -A ARCH=([amd64]="x86_64" [arm64]="aarch64")

export PATH="$SNAP/usr/sbin:$SNAP/usr/bin:$SNAP/sbin:$SNAP/bin:$PATH"

if [[ -z "${SNAP_ARCH:-}" ]]; then
    SNAP_ARCH=$(dpkg --print-architecture 2>/dev/null || echo "amd64")
fi

export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$SNAP/lib:$SNAP/usr/lib:$SNAP/lib/${ARCH[$SNAP_ARCH]}-linux-gnu:$SNAP/usr/lib/${ARCH[$SNAP_ARCH]}-linux-gnu"
export LD_LIBRARY_PATH="$SNAP_LIBRARY_PATH:$LD_LIBRARY_PATH"
export PYTHONPATH="$SNAP/usr/lib/python3/dist-packages:$SNAP/usr/lib/python3.10/dist-packages:$SNAP/usr/lib/python3/site-packages:$SNAP/usr/lib/python3.10/site-packages:${PYTHONPATH:-}"
