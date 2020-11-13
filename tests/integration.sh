#!/bin/bash

if [ $# -gt 0 ]
then
    target="$1"
else
    target="http://127.0.0.1:5000"
fi

function run() {
    address=$1
    keyword=$2
    echo "Testing grepping $keyword on page $address" 
    wget -O - $target/$address 2>/dev/null | grep -F "$keyword" >/dev/null
    if [ $? -ne 0 ]
    then
        echo "*** Test failed: grep $keyword on page $address"
    fi
}

run "/vendorlist?id=60" "data: [0,"
run "/vendorlist?id=-2" "Error"
run "/vendorlist?id=sdklfjs" "Error"
run "/vendorlist?id=9000" "Error"
