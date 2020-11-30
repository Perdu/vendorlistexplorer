#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Web app main script
# You need Flask to run this script

import json
import datetime
import calendar
import decimal
import html

from flask import Flask, render_template, request, url_for, send_from_directory, Response

from utils import *
from database import *

app = Flask(__name__)
config = parse_config_file(CONFIG_FILE)
app.debug = config.is_debug_activated
db = None

def execute(query, parameters = None, return_rowcount = False, return_rows = False):
    cur = db.cursor()
    cur.execute(query, parameters)
    if return_rowcount:
        res = cur.rowcount
    elif return_rows:
        res = cur.fetchall()
    else:
        res = cur.fetchone()
    cur.close()
    return res

def get_series(vendorlist_id, series_type):
    res = ""
    if series_type == "consent":
        query = "SELECT COUNT(*), purpose FROM vendor_purpose WHERE vendorlist_id = %d GROUP BY purpose ORDER BY purpose" % int(vendorlist_id)
    elif series_type == "legint":
        query = "SELECT COUNT(*), legint FROM vendor_legint WHERE vendorlist_id = %d GROUP BY legint ORDER BY legint" % int(vendorlist_id)
    elif series_type == "flexible_purpose":
        query = "SELECT COUNT(*), flexible_purpose FROM vendor_flexible_purpose WHERE vendorlist_id = %d GROUP BY flexible_purpose ORDER BY flexible_purpose" % int(vendorlist_id)
    elif series_type == "special_purpose":
        query = "SELECT COUNT(*), special_purpose FROM vendor_special_purpose WHERE vendorlist_id = %d GROUP BY special_purpose ORDER BY special_purpose" % int(vendorlist_id)
    elif series_type == "feature":
        query = "SELECT COUNT(*), feature FROM vendor_feature WHERE vendorlist_id = %d GROUP BY feature ORDER BY feature" % int(vendorlist_id)
    elif series_type == "special_feature":
        query = "SELECT COUNT(*), special_feature FROM vendor_special_feature WHERE vendorlist_id = %d GROUP BY special_feature ORDER BY special_feature" % int(vendorlist_id)
    rows = execute(query, return_rows=True)
    i = 1
    for row in rows:
        while row[1] != i: # missing case (ex: purpose 1)
            res = res + "0,"
            i += 1
        count = row[0]
        res = res + "%d," % int(count)
        i += 1
    res = res.rstrip(",")
    return res

def get_vendors(vendorlist_id, category, purpose_id, feature_id, special_feature_id, special_purpose_id):
    res = ""
    if purpose_id != -1:
        if category == 0:
            query = "SELECT name, url, cookieMaxAgeSeconds, usesNonCookieAccess, vendor.id FROM vendor LEFT JOIN vendor_purpose ON vendor.id=vendor_purpose.vendor_id AND vendor.vendorlist_id=vendor_purpose.vendorlist_id WHERE vendor.vendorlist_id = %d AND purpose = %d ORDER BY name" % (int(vendorlist_id), int(purpose_id))
        elif category == 1:
            query = "SELECT name, url, cookieMaxAgeSeconds, usesNonCookieAccess, vendor.id FROM vendor LEFT JOIN vendor_legint ON vendor.id=vendor_legint.vendor_id AND vendor.vendorlist_id=vendor_legint.vendorlist_id WHERE vendor.vendorlist_id = %d AND legint = %d ORDER BY name" % (int(vendorlist_id), int(purpose_id))
        elif category == 2:
            query = "SELECT name, url, cookieMaxAgeSeconds, usesNonCookieAccess, vendor.id FROM vendor LEFT JOIN vendor_flexible_purpose ON vendor.id=vendor_flexible_purpose.vendor_id AND vendor.vendorlist_id=vendor_flexible_purpose.vendorlist_id WHERE vendor.vendorlist_id = %d AND flexible_purpose = %d ORDER BY name" % (int(vendorlist_id), int(purpose_id))
    elif feature_id != -1:
        query = "SELECT name, url, cookieMaxAgeSeconds, usesNonCookieAccess, vendor.id FROM vendor LEFT JOIN vendor_feature ON vendor.id=vendor_feature.vendor_id AND vendor.vendorlist_id=vendor_feature.vendorlist_id WHERE vendor.vendorlist_id = %d AND feature = %d ORDER BY name" % (int(vendorlist_id), int(feature_id))
    elif special_feature_id != -1:
        query = "SELECT name, url, cookieMaxAgeSeconds, usesNonCookieAccess, vendor.id FROM vendor LEFT JOIN vendor_special_feature ON vendor.id=vendor_special_feature.vendor_id AND vendor.vendorlist_id=vendor_special_feature.vendorlist_id WHERE vendor.vendorlist_id = %d AND special_feature = %d ORDER BY name" % (int(vendorlist_id), int(special_feature_id))
    else:
        query = "SELECT name, url, cookieMaxAgeSeconds, usesNonCookieAccess, vendor.id FROM vendor LEFT JOIN vendor_special_purpose ON vendor.id=vendor_special_purpose.vendor_id AND vendor.vendorlist_id=vendor_special_purpose.vendorlist_id WHERE vendor.vendorlist_id = %d AND special_purpose = %d ORDER BY name" % (int(vendorlist_id), int(special_purpose_id))
    rows = execute(query, return_rows = True)
    return json.dumps(rows)

def add_purpose_to_vendor_dict(vendor, purpose_type, vendorlist_id, vendor_id):
    query = "SELECT %s FROM vendor_%s WHERE vendorlist_id = %d AND vendor_id = %d" % (purpose_type, purpose_type, int(vendorlist_id), int(vendor_id))
    rows = execute(query, return_rows = True)
    vendor[purpose_type] = []
    for row in rows:
        vendor[purpose_type].append(row[0])

def get_vendor(vendorlist_id, vendor_id):
    res = ""
    vendor = {}
    query = "SELECT name, url, cookieMaxAgeSeconds, usesNonCookieAccess FROM vendor WHERE vendorlist_id = %d AND id = %d ORDER BY name" % (int(vendorlist_id), int(vendor_id))
    row = execute(query)
    vendor["name"] = row[0]
    vendor["url"] = row[1]
    vendor["cookieMaxAgeSeconds"] = int(row[2])
    vendor["usesNonCookieAccess"] = int(row[3])
    add_purpose_to_vendor_dict(vendor, "purpose", vendorlist_id, vendor_id)
    add_purpose_to_vendor_dict(vendor, "legint", vendorlist_id, vendor_id)
    add_purpose_to_vendor_dict(vendor, "flexible_purpose", vendorlist_id, vendor_id)
    add_purpose_to_vendor_dict(vendor, "special_purpose", vendorlist_id, vendor_id)
    add_purpose_to_vendor_dict(vendor, "feature", vendorlist_id, vendor_id)
    add_purpose_to_vendor_dict(vendor, "special_feature", vendorlist_id, vendor_id)
    return json.dumps(vendor)

def get_latest_vendorlist():
    row = execute("SELECT MAX(id) FROM vendorlist")
    return int(row[0])

def get_max_vendorid():
    row = execute("SELECT MAX(id) FROM vendor")
    return int(row[0])

def error():
    return render_template("error.html")

def get_select_options(current_vendorlist):
    res = ""
    rows = execute("SELECT id FROM vendorlist", return_rows=True)
    for row in rows:
        vendorlist_id = int(row[0])
        if vendorlist_id == int(current_vendorlist):
            selected = "selected"
        else:
            selected = ""
        res = res + "<option value=\"%d\" %s>%d</option>\n" % (vendorlist_id, selected, vendorlist_id)
    return res

def get_date(vendorlist_id):
    row = execute("SELECT lastUpdated FROM vendorlist WHERE id = %d" % vendorlist_id)
    return row[0].strftime("%Y-%m-%d")

def get_int_param(name, max_val=0, default_val=-1):
    try:
        res = request.args.get(name, None)
        if (res is None):
            return default_val
        res = int(res)
        if res < 0:
            return -1
        if max_val > 0 and res > max_val:
            return -1
        return res
    except ValueError:
        return -1

@app.route('/', methods=['POST', 'GET'])
@app.route('/vendorlist', methods=['POST', 'GET'])
def disp_vendorlist():
    latest_vendor_list = get_latest_vendorlist()
    vendorlist_id = get_int_param('id', max_val=latest_vendor_list, default_val=latest_vendor_list)
    if vendorlist_id == -1:
        return error()
    if vendorlist_id is None:
        vendorlist_id = latest_vendor_list
    purpose_series = get_series(vendorlist_id, "consent")
    legint_series = get_series(vendorlist_id, "legint")
    flexible_series = get_series(vendorlist_id, "flexible_purpose")
    special_purpose_series = get_series(vendorlist_id, "special_purpose")
    feature_series = get_series(vendorlist_id, "feature")
    special_feature_series = get_series(vendorlist_id, "special_feature")
    select_options = get_select_options(vendorlist_id)
    date = get_date(vendorlist_id)
    return render_template("vendorlist.html", vendorlist_id=vendorlist_id, purpose_series=purpose_series, legint_series=legint_series, flexible_series=flexible_series, special_purpose_series=special_purpose_series, feature_series=feature_series, special_feature_series=special_feature_series, select_options=select_options, date=date)

@app.route('/vendors', methods=['POST', 'GET'])
def disp_vendors():
    latest_vendor_list = get_latest_vendorlist()
    vendorlist_id = get_int_param('vendorlistid', max_val=latest_vendor_list)
    consent_purpose_id = get_int_param('consentpurposeid', max_val=10)
    feature_id = get_int_param('featureid', max_val=3)
    special_feature_id = get_int_param('specialfeatureid', max_val=3)
    special_purpose_id = get_int_param('specialpurposeid', max_val=3)
    category = get_int_param('categ', max_val=3)
    if consent_purpose_id == -1 and feature_id == -1 and special_feature_id == -1 and special_purpose_id == -1:
        return error()
    if vendorlist_id == -1 or category == -1:
        return error()
    if vendorlist_id is None:
        vendorlist_id = get_latest_vendorlist()
    vendors_details = get_vendors(vendorlist_id, category, consent_purpose_id, feature_id, special_feature_id, special_purpose_id)
    return Response(vendors_details, mimetype='application/json')

@app.route('/vendor', methods=['POST', 'GET'])
def disp_vendor():
    latest_vendor_list = get_latest_vendorlist()
    max_vendor_id = get_max_vendorid()
    vendorlist_id = get_int_param('vendorlistid', max_val=latest_vendor_list)
    vendor_id = get_int_param('id', max_val=max_vendor_id)
    vendor_details = get_vendor(vendorlist_id, vendor_id)
    return Response(vendor_details, mimetype='application/json')

@app.route('/robots.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

@app.before_request
def before_request():
    global db
    if request.endpoint not in ('static', None):
        db = start_db()

@app.after_request
def after_request(res):
    if request.endpoint not in ('static', None):
        if db is not None:
            db.close()
    return res

if __name__ == "__main__":
    app.run(host=config.host)


