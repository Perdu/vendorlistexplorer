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

def disp_graph(rows):
    res = ""
    p = player()
    p.reset()
    for row in rows:
        if isinstance(row[0], int):
            name = str(row[0])
        else:
            name = html.escape(row[0])
        #    name = unicode(row[0], errors='ignore')
        if name != p.name and p.name != "":
            res = res + "{ name: " + "'" + p.name + "'" + ", data:" + json.dumps(p.data, default=decimal_default) + "},\n"
            p.reset()
        p.name = name
        score = []
        score.append(calendar.timegm(row[1].utctimetuple())*1000)
        score.append(row[2])
        p.data.append(score)
        # last player
    res = res + "{ name: " + "'" + p.name + "'" + ", data:" + json.dumps(p.data, default=decimal_default) + "}"
    return res

@app.route('/vendorlist', methods=['POST', 'GET'])
def disp_vendorlist():
    vendorlist_id = request.args.get('id', '')
    return render_template("vendorlist.html", vendorlist_id=vendorlist_id)

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


