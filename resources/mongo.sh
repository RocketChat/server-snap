#! /bin/sh

start() {
	LC_ALL=C mongod --bind_ip 127.0.0.1 --port 27017 \
		--pidfilepath $SNAP_COMMON/mongod.pid \
		--logpath=$SNAP_COMMON/mongod.log --logRotate=reopen --logAppend=true \
		--dbpath=$SNAP_COMMON \
		--smallfiles --journal --replSet rs0 \
		--fork
}

stop() {
	LC_ALL=C mongod --dbpath=$SNAP_COMMON --shutdown
}

logs() {
	tail -f $SNAP_COMMON/mongod.log
}

shell() {
	LC_ALL=C mongo
}

if [ -z "$1" ]; then
	shell
else
	eval "${1#--}"
fi
