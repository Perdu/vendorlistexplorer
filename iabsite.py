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

def get_purpose_series(vendorlist_id):
    res_purposes = ""
    rows = execute("SELECT COUNT(*), purpose FROM vendor_purpose WHERE vendorlist_id = %d GROUP BY purpose ORDER BY purpose" % int(vendorlist_id), return_rows=True)
    for row in rows:
        count = row[0]
        res_purposes = res_purposes + "%d," % int(count)
    res_purposes = res_purposes.rstrip(",")
    return res_purposes

def get_legint_series(vendorlist_id):
    res_legint = ""
    rows = execute("SELECT COUNT(*), legint FROM vendor_legint WHERE vendorlist_id = %d GROUP BY legint ORDER BY legint" % int(vendorlist_id), return_rows=True)
    i = 1
    for row in rows:
        while row[1] != i: # missing case (ex: purpose 1)
            res_legint = res_legint + "0,"
            i += 1
        count = row[0]
        res_legint = res_legint + "%d," % int(count)
        i += 1
    res_legint = res_legint.rstrip(",")
    return res_legint

def get_vendors(vendorlist_id, consent_purpose_id):
    res = ""
    rows = execute("SELECT name, url FROM vendor LEFT JOIN vendor_purpose ON vendor.id=vendor_purpose.vendor_id AND vendor.vendorlist_id=vendor_purpose.vendorlist_id WHERE vendor.vendorlist_id = %d AND purpose = %d ORDER BY name" % (int(vendorlist_id), int(consent_purpose_id)), return_rows = True)
    return json.dumps(rows)

def get_latest_vendorlist():
    row = execute("SELECT MAX(id) FROM vendorlist")
    return int(row[0])

@app.route('/vendorlist', methods=['POST', 'GET'])
def disp_vendorlist():
    vendorlist_id = request.args.get('id', None)
    if vendorlist_id is None:
        vendorlist_id = get_latest_vendorlist()
    purpose_series = get_purpose_series(vendorlist_id)
    legint_series = get_legint_series(vendorlist_id)
    return render_template("vendorlist.html", vendorlist_id=vendorlist_id, purpose_series=purpose_series, legint_series=legint_series)

@app.route('/vendors', methods=['POST', 'GET'])
def disp_vendors():
    vendorlist_id = request.args.get('vendorlistid', None)
    consent_purpose_id = request.args.get('consentpurposeid', None)
    if vendorlist_id is None:
        vendorlist_id = get_latest_vendorlist()
    vendors_details = get_vendors(vendorlist_id, consent_purpose_id)
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


