#!/bin/bash

error() {
  printf "[ERROR] %s\n" "$*" >&2
  exit 1
}
