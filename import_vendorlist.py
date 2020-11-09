#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json

from database import *
from utils import *

def import_vendor_list(vendorlist_file):
    with open(vendorlist_file) as json_file:
        vendorlist = json.load(json_file)
        return vendorlist

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_vendorlist.py VENDORLIST")
        sys.exit(1)
    vendorlist = import_vendor_list(sys.argv[1])
    db = start_db_orm()
    vendorlist_id = int(vendorlist["vendorListVersion"])
    vendorlist_t = Vendorlist(vendorlist_id)
    db.add(vendorlist_t)
    db.commit()
    for vendor_id in vendorlist["vendors"]:
        vendor = vendorlist["vendors"][vendor_id]
        vendor_t = Vendor((int(vendor["id"])), vendorlist_id)
        vendor_t.name = vendor["name"]
        vendor_t.url = vendor["policyUrl"]
        db.add(vendor_t)
        db.commit()
        for purpose in vendor["purposes"]:
            purpose_t = Vendor_purpose(vendor_id, vendorlist_id, purpose)
            db.add(purpose_t)
        for legint in vendor["legIntPurposes"]:
            purpose_t = Vendor_legint(vendor_id, vendorlist_id, legint)
            db.add(purpose_t)
        for flexible_purpose in vendor["flexiblePurposes"]:
            purpose_t = Vendor_flexible_purpose(vendor_id, vendorlist_id, flexible_purpose)
            db.add(purpose_t)
        for special_purpose in vendor["specialPurposes"]:
            purpose_t = Vendor_special_purpose(vendor_id, vendorlist_id, special_purpose)
            db.add(purpose_t)
        for feature in vendor["features"]:
            purpose_t = Vendor_feature(vendor_id, vendorlist_id, feature)
            db.add(purpose_t)
        for special_feature in vendor["specialFeatures"]:
            purpose_t = Vendor_special_feature(vendor_id, vendorlist_id, special_feature)
            db.add(purpose_t)
        db.commit()
    db.commit()
