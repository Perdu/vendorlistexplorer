#!/bin/bash

all_ok=0

if [ $# -gt 0 ]
then
    target="$1"
else
    target="http://127.0.0.1:5000"
fi

function run() {
    address=$1
    keyword=$2
    wget -O - $target/$address 2>/dev/null | grep -F "$keyword" >/dev/null
    if [ $? -ne 0 ]
    then
        echo "*** Test failed: grep $keyword on page $address"
        all_ok=1
    fi
}

echo "Testing vendorlist"
run "/vendorlist?id=60" "data: [0,"

echo "Testing vendorlist?id"
run "/vendorlist?id=-2" "Error"
run "/vendorlist?id=sdklfjs" "Error"
run "/vendorlist?id=9000" "Error"
run "/vendorlist" "data: [0,"

echo "Testing vendors"
run "/vendors?vendorlistid=60&consentpurposeid=8&categ=0" "1020, Inc."

echo "Testing vendors?vendorlistid"
run "/vendors?vendorlistid=-1&consentpurposeid=8&categ=0" "Error"
run "/vendors?vendorlistid=sdklfj&consentpurposeid=8&categ=0" "Error"
run "/vendors?vendorlistid=9000&consentpurposeid=8&categ=0" "Error"
run "/vendors?consentpurposeid=8&categ=0" "Error"

echo "Testing vendors?consentpurposeid"
run "/vendors?vendorlistid=60&consentpurposeid=-1&categ=0" "Error"
run "/vendors?vendorlistid=60&consentpurposeid=sdkfl&categ=0" "Error"
run "/vendors?vendorlistid=60&consentpurposeid=9000&categ=0" "Error"
run "/vendors?consentpurposeid=-1&categ=0" "Error"

echo "Testing vendors?categ"
run "/vendors?vendorlistid=60&consentpurposeid=8&categ=-1" "Error"
run "/vendors?vendorlistid=60&consentpurposeid=8&categ=sdfkljsd" "Error"
run "/vendors?vendorlistid=60&consentpurposeid=8&categ=9000" "Error"
run "/vendors?vendorlistid=60&consentpurposeid=8" "Error"

exit $all_ok
