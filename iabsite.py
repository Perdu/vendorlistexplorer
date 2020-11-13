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

def get_vendors(vendorlist_id, purpose_id, category):
    res = ""
    if category == 0:
        query = "SELECT name, url FROM vendor LEFT JOIN vendor_purpose ON vendor.id=vendor_purpose.vendor_id AND vendor.vendorlist_id=vendor_purpose.vendorlist_id WHERE vendor.vendorlist_id = %d AND purpose = %d ORDER BY name" % (int(vendorlist_id), int(purpose_id))
    elif category == 1:
        query = "SELECT name, url FROM vendor LEFT JOIN vendor_legint ON vendor.id=vendor_legint.vendor_id AND vendor.vendorlist_id=vendor_legint.vendorlist_id WHERE vendor.vendorlist_id = %d AND legint = %d ORDER BY name" % (int(vendorlist_id), int(purpose_id))
    elif category == 2:
        query = "SELECT name, url FROM vendor LEFT JOIN vendor_flexible_purpose ON vendor.id=vendor_flexible_purpose.vendor_id AND vendor.vendorlist_id=vendor_flexible_purpose.vendorlist_id WHERE vendor.vendorlist_id = %d AND flexible_purpose = %d ORDER BY name" % (int(vendorlist_id), int(purpose_id))
    rows = execute(query, return_rows = True)
    return json.dumps(rows)

def get_latest_vendorlist():
    row = execute("SELECT MAX(id) FROM vendorlist")
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

def get_int_param(name, max_val=0):
    try:
        res = int(request.args.get(name, None))
        if res < 0:
            return -1
        if max_val > 0 and res > max_val:
            return -1
        return res
    except ValueError:
        return -1

@app.route('/vendorlist', methods=['POST', 'GET'])
def disp_vendorlist():
    latest_vendor_list = get_latest_vendorlist()
    vendorlist_id = get_int_param('id', max_val=latest_vendor_list)
    if vendorlist_id == -1:
        return error()
    if vendorlist_id is None:
        vendorlist_id = latest_vendor_list
    purpose_series = get_series(vendorlist_id, "consent")
    legint_series = get_series(vendorlist_id, "legint")
    flexible_series = get_series(vendorlist_id, "flexible_purpose")
    select_options = get_select_options(vendorlist_id)
    return render_template("vendorlist.html", vendorlist_id=vendorlist_id, purpose_series=purpose_series, legint_series=legint_series, flexible_series=flexible_series, select_options=select_options)

@app.route('/vendors', methods=['POST', 'GET'])
def disp_vendors():
    latest_vendor_list = get_latest_vendorlist()
    vendorlist_id = get_int_param('vendorlistid', max_val=latest_vendor_list)
    consent_purpose_id = get_int_param('consentpurposeid', max_val=10)
    category = get_int_param('categ', max_val=3)
    if vendorlist_id == -1 or consent_purpose_id == -1 or category == -1:
        return error()
    if vendorlist_id is None:
        vendorlist_id = get_latest_vendorlist()
    vendors_details = get_vendors(vendorlist_id, consent_purpose_id, category)
    return Response(vendors_details, mimetype='application/json')

@app.route('/robots.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

@app.route("/")
def index():
    vendorlists = Vendorlist.query.all()
    return render_template("index.html", version=versions)

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


