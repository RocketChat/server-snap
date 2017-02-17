#! /bin/bash

export BABEL_CACHE_DIR=/tmp
export PORT=3000
export ROOT_URL=http://localhost
export MONGO_URL=mongodb://localhost:27017/parties
export MONGO_OPLOG_URL=mongodb://localhost:27017/local?replicaSet=rcreplset
export Accounts_AvatarStorePath=$SNAP_COMMON/uploads

node $SNAP/main.js

while [[ $? == 1 ]]
do
    sleep 5
    node $SNAP/main.js
done

