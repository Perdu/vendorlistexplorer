#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from urllib.parse import urlparse
from urllib3.exceptions import MaxRetryError
import csv
import subprocess
import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.conf')

def import_iab_cmp_list(short_names=False):
    CMP = {}
    if short_names:
        f = "cmplist/IAB_CMP_list_full.csv"
    else:
        f = 'cmplist/IAB_CMP_list_full_fullnames.csv'
    reader = csv.reader(open(f, 'r'))
    first_line = True
    for row in reader:
        if first_line:
            first_line = False
            continue
        cmp_id = row[0]
        name = row[1]
        CMP[int(cmp_id)] = name
    return CMP

def decode_consent_string(consent_string):
    proc = subprocess.Popen(['node', 'decode_IAB_API_strings.js' , consent_string], stdout=subprocess.PIPE)
    (out, err) = proc.communicate()
    if proc.returncode != 0:
        print("Unable to decode consent string.")
        return None
    return json.loads(out)

def get_vendor_list(vendorlist_id=163):
    with open('vendorlist/vendorlist_%d.json' % int(vendorlist_id)) as json_file:
        vendorlist = json.load(json_file)
        return vendorlist

class Config():
    def __init__(self, c):
        self.db_name = c.get('Database', 'db_name')
        self.db_server = c.get('Database', 'db_server')
        self.db_user = c.get('Database', 'db_user')
        self.db_pass = c.get('Database', 'db_pass')
        self.is_debug_activated = c.get('Other', 'is_debug_activated')
        self.host = c.get('Other', 'host')
