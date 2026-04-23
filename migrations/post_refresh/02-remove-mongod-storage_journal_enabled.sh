#!/bin/bash

>/dev/null cat <<CommentEnd

storage:
  journal:
    enabled: <true|false>

is no longer a supported config flag; having it breaks mongod startup.

CommentEnd

start() {
  python3 -c '
import sys

from ruamel.yaml import YAML
yaml = YAML()
# important since mongod.conf is user editable, we want to preserve their comments;
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=2, offset=0)

mongod_conf = {}
with open(sys.argv[1], "r") as f:
  mongod_conf = yaml.load(f)

  
if "storage" in mongod_conf and "journal" in mongod_conf["storage"]:
  del mongod_conf["storage"]["journal"]
  if not mongod_conf["storage"]:
    del mongod_conf["storage"]

with open(sys.argv[1], "w") as f:
  yaml.dump(mongod_conf, f)
  ' $SNAP_DATA/mongod.conf
}
