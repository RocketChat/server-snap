#! /bin/bash

exec 3>&1

files=($(find migrations -executable -type f))
options=()
index=1

for file in ${files[@]}; do
	options+=("$index ${file#migrations/} off")
	declare -p options
	((index++))
done

indexes=$(dialog \
	--nocancel --extra-button --extra-label disable --ok-label enable \
	--checklist "Migrations" 0 0 ${#options[@]} ${options[@]} \
	2>&1 1>&3)

case $? in
	0)
		clear
		set -x
		for index in $indexes; do
			chmod +x migrations/${files[$(($index-1))]}
		done
		;;
	3)
		clear
		set -x
		for index in $indexes; do
			chmod -x migrations/${files[$(($index-1))]}
		done
		;;
esac

exec 3>&-
