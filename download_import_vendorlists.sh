#!/bin/bash

function download_vl() {
    wget -O vendorlists/vendorlistv2_"$1".json https://vendor-list.consensu.org/v2/archives/vendor-list-v"$1".json
    return $?
}

function download_and_add() {
    download_vl "$1"
    res=$?
    if [ $res == 0 ]
    then
        python import_vendorlist.py vendorlists/vendorlistv2_"$1".json
    fi
    return $res
}

cd "$(dirname "$0")";
mkdir -p "vendorlists"

if [ "$#" == "0" ]
then
    # download all latest v2 vendorlists
    latest_vendorlist_number=$(ls -1 vendorlists/ | grep vendorlist | sed 's/vendorlistv2_\(.*\)\.json/\1/' | sort -g | tail -n 1)
    if [ "$latest_vendorlist_number" == "" ]
    then
        latest_vendorlist_number=0
    fi
    res=0
    while [ $res == 0 ]
    do
        latest_vendorlist_number=$(( $latest_vendorlist_number + 1 ))
        download_and_add "$latest_vendorlist_number"
        res=$?
    done
    rm vendorlists/vendorlistv2_"$latest_vendorlist_number".json
else
    # download vendorlist given in argument
    download_and_add "$1"
fi
