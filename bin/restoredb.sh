#! /bin/bash

if [[ ${EUID} != 0 ]]
then
    echo "[-] This task must be run with 'sudo'."
    exit
fi

if [[ ! -f ${1} ]]
then
    echo "[-] Usage: snap run rocketchat-server.rcrestore ${SNAP_COMMON}/backup_file.tgz"
    exit
fi

cd ${1%/*}
if [[ -z $(pwd | grep "${SNAP_COMMON}") ]]
then
    echo "[-] Backup file must be within ${SNAP_COMMON}."
    exit
fi

function ask_backup {
    echo -n "\
*** ATTENTION ***
* Your current database WILL BE DROPPED prior to the restore!
* Would you like to make a backup of the current database before proceeding?
* (y/n/Q)> "

    read choice
    [[ "${choice,,}" = n* ]] && return
    [[ "${choice,,}" = y* ]] && rcbackup && return
    exit
}

function abort {
        echo "[!] ${1}"
        echo "[*] Check ${restore_dir}/${log_name} for details."
        echo "[-] Restore aborted!"
        exit
}

mongo parties --eval "db.getCollectionNames()" | grep "\[ \]" >> /dev/null || ask_backup

echo "[*] Extracting backup file..."
restore_dir="${SNAP_COMMON}/restore"
log_name="extraction.log"
mkdir -p ${restore_dir}
cd ${restore_dir}
tar --no-same-owner --overwrite -zxvf ${1} &> "${restore_dir}/${log_name}"
if [[ $? != 0 ]]
then
    abort "Failed to extract backup files to ${restore_dir}!"
    exit
fi

echo "[*] Restoring data..."
data_dir=$(tail -n 1 /var/snap/rocketchat-server/common/restore/extraction.log)
data_dir=$(dirname ${data_dir})
log_name="mongorestore.log"
mongorestore --db parties --noIndexRestore --drop ${data_dir} &> "${restore_dir}/${log_name}"
if [[ $? != 0 ]]
then
    abort "Failed to execute mongorestore from ${data_dir}!"
    exit
fi

echo "[*] Preparing database..."
log_name="mongoprepare.log"
mongo parties --eval "db.repairDatabase()" --verbose &> "${restore_dir}/${log_name}"
if [[ $? != 0 ]]
then
    abort "Failed to prepare database for usage!"
    exit
fi

echo "[+] Restore completed! Please restart the snap.rocketchat services to verify."

