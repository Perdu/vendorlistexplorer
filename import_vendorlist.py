#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import datetime
import html

from database import *
from utils import *

def import_vendor_list(vendorlist_file):
    with open(vendorlist_file) as json_file:
        vendorlist = json.load(json_file)
        return vendorlist

def vendorlist_exists(db, vendorlist_id):
    vendorlist = db.query(Vendorlist).filter_by(id=vendorlist_id).scalar()
    if vendorlist:
        return True
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_vendorlist.py VENDORLIST")
        sys.exit(1)
    vendorlist = import_vendor_list(sys.argv[1])
    db = start_db_orm()
    vendorlist_id = int(vendorlist["vendorListVersion"])
    if vendorlist_exists(db, vendorlist_id):
        print("Vendorlist already in database. Exiting.")
        sys.exit(1)
    lastUpdated = datetime.datetime.strptime(vendorlist["lastUpdated"], "%Y-%m-%dT%H:%M:%SZ")
    vendorlist_t = Vendorlist(vendorlist_id, lastUpdated)
    db.add(vendorlist_t)
    db.commit()
    for vendor_id in vendorlist["vendors"]:
        vendor = vendorlist["vendors"][vendor_id]
        vendor_t = Vendor((int(vendor["id"])), vendorlist_id)
        vendor_t.name = html.escape(vendor["name"])
        vendor_t.url = html.escape(vendor["policyUrl"])
        if "cookieMaxAgeSeconds" in vendor:
            vendor_t.cookieMaxAgeSeconds = int(vendor["cookieMaxAgeSeconds"])
        if "usesNonCookieAccess" in vendor:
            vendor_t.usesNonCookieAccess = int(vendor["usesNonCookieAccess"])
        db.add(vendor_t)
        db.commit()
        for purpose in vendor["purposes"]:
            purpose_t = Vendor_purpose(vendor_id, vendorlist_id, int(purpose))
            db.add(purpose_t)
        for legint in vendor["legIntPurposes"]:
            purpose_t = Vendor_legint(vendor_id, vendorlist_id, int(legint))
            db.add(purpose_t)
        for flexible_purpose in vendor["flexiblePurposes"]:
            purpose_t = Vendor_flexible_purpose(vendor_id, vendorlist_id, int(flexible_purpose))
            db.add(purpose_t)
        for special_purpose in vendor["specialPurposes"]:
            purpose_t = Vendor_special_purpose(vendor_id, vendorlist_id, int(special_purpose))
            db.add(purpose_t)
        for feature in vendor["features"]:
            purpose_t = Vendor_feature(vendor_id, vendorlist_id, int(feature))
            db.add(purpose_t)
        for special_feature in vendor["specialFeatures"]:
            purpose_t = Vendor_special_feature(vendor_id, vendorlist_id, int(special_feature))
            db.add(purpose_t)
        db.commit()
    db.commit()
