#!/bin/bash

if [ $# -ne 1 ]
then
    echo "Usage: $0 VENDORLIST_ID"
    exit
fi

id=$1

echo "Deleting vendorlist $id"

sudo mysql -u root -v iabsite -e "SET FOREIGN_KEY_CHECKS=0;\
delete from vendor_feature where vendorlist_id = $id; \
delete from vendor_flexible_purpose where vendorlist_id = $id;\
delete from vendor_legint where vendorlist_id = $id;\
delete from vendor_purpose where vendorlist_id = $id;\
delete from vendor_special_feature where vendorlist_id = $id;\
delete from vendor_special_purpose where vendorlist_id = $id;\
delete from vendor where vendorlist_id = $id;\
delete from vendorlist where id = $id;\
SET FOREIGN_KEY_CHECKS=1;
"
