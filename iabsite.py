#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Web app main script
# You need Flask to run this script

import json
import datetime
import calendar
import decimal
import html

from flask import Flask, render_template, request, url_for, send_from_directory

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

def purpose_number_to_name(nb):
    if nb == 1:
        return "Store and/or access information on a device"
    elif nb == 2:
        return "Select basic ads"
    elif nb == 3:
        return "Create a personalised ads profile"
    elif nb == 4:
        return "Select personalised ads"
    elif nb == 5:
        return "Create a personalised content profile"
    elif nb == 6:
        return "Select personalised content"
    elif nb == 7:
        return "Measure ad performance"
    elif nb == 8:
        return "Measure content performance"
    elif nb == 9:
        return "Apply market research to generate audience insights"
    elif nb == 10:
        return "Develop and improve product"

def get_purpose_series(vendorlist_id):
    res = ""
    rows = execute("SELECT COUNT(*), purpose FROM vendor_purpose WHERE vendorlist_id = %d GROUP BY purpose" % int(vendorlist_id), return_rows=True)
    for row in rows:
        count = row[0]
        purpose = purpose_number_to_name(int(row[1]))
        res = res + "\n{ name: \"%s\", data: [%d] }," % (purpose, int(count))
    res = res.rstrip(",")
    return res

@app.route('/vendorlist', methods=['POST', 'GET'])
def disp_vendorlist():
    vendorlist_id = request.args.get('id', '')
    purpose_series = get_purpose_series(vendorlist_id)
    return render_template("vendorlist.html", vendorlist_id=vendorlist_id, purpose_series=purpose_series)

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


