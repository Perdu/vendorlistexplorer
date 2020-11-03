#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from urllib.parse import urlparse
from urllib3.exceptions import MaxRetryError
import csv
import subprocess
import json

CONFIG_FILE = 'config.conf'

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
