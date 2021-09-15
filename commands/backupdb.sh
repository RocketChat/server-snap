#!/bin/bash

if (( $EUID )); then
    echo "[-] This task must be run with 'sudo'." >&2
    exit 1
fi

if [[ -f $SNAP_COMMON/rocketchat.pid ]]; then
    echo "[-] Please shutdown Rocket.Chat first to get a clean backup" >&2
    echo "[-] Use 'sudo snap stop rocketchat-server.rocketchat-server'" >&2
fi

TIMESTAMP=$(date +"%Y%m%d.%H%M")
BACKUP_DIR=$SNAP_COMMON/backup
BACKUP_FILE=$BACKUP_DIR/rocketchat_backup_$TIMESTAMP.tar.gz
LOG=$BACKUP_DIR/backup_$TIMESTAMP.log
DUMP_DIR=$BACKUP_DIR/dump

[[ -d $BACKUP_DIR ]] || mkdir $BACKUP_DIR
[[ -d $DUMP_DIR ]] && rm -rf $DUMP_DIR
[[ -f $BACKUP_FILE ]] && rm -rf $BACKUP_FILE
[[ -f $LOG ]] && rm -f $LOG

log "[*] Creating backup file..."
mkdir $DUMP_DIR
log "[*] Dumping database with \"mongodump -d parties -o $DUMP_DIR\""
mongodump -d parties -o $DUMP_DIR &>> $LOG
log "[*] Packing archive with \"tar czvf $BACKUP_FILE $DUMP_DIR\""
tar czvf $BACKUP_FILE -C $BACKUP_DIR dump
rm -rf $DUMP_DIR

echo "[+] A backup of your data can be found at $BACKUP_FILE"
