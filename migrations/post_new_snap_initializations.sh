cat >$SNAP_DATA/mongod.conf <<EOF

# For documentation of all options, see:
#   http://docs.mongodb.org/manual/reference/configuration-options/

# processManagement::fork and systemlog::* are ignored

net:
  bindIp: 127.0.0.1
  port: 27017

setParameter:
  enableLocalhostAuthBypass: false

storage:
  dbPath: $SNAP_COMMON
  journal:
    enabled: true

systemLog:
  destination: syslog

replication:
  replSetName: rs0

processManagement:
  pidFilePath: $SNAP_COMMON/mongod.pid

EOF

port=$(snapctl get port)
[[ -z $port ]] && snapctl set port=3000
url=$(snapctl get caddy-url)
[[ -z $url ]] && url=$(snapctl get siteurl)
[[ -n $url ]] && snapctl set siteurl=$url || snapctl set siteurl=http://localhost:$port

[[ -z $(snapctl get mongo-url) ]] && snapctl set mongo-url=mongodb://localhost:27017/parties
[[ -z $(snapctl get mongo-oplog-url) ]] && snapctl set mongo-oplog-url=mongodb://localhost:27017/local
[[ -z $(snapctl get backup-on-refresh) ]] && snapctl set backup-on-refresh=disable

snapctl unset snap-refreshing
snapctl unset caddy
snapctl unset caddy-url
snapctl unset https
snapctl unset db-feature-compatibility-version
