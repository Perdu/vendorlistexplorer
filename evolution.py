#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script generates graphs showing the evolution of declaration of purposes
# using matplotlib

import sys
import json
import datetime

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from utils import *
from database import *

config = parse_config_file(CONFIG_FILE)
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

def compute_evolution(purpose_number):
    counts = []
    dates = []
    query = "SELECT COUNT(*), lastUpdated FROM vendor_legint LEFT JOIN vendorlist ON vendor_legint.vendorlist_id = vendorlist.id WHERE legint = %d GROUP BY vendorlist_id \
             UNION SELECT 0, lastUpdated FROM vendorlist WHERE id NOT IN (SELECT vendorlist_id FROM vendor_legint WHERE legint = %d AND vendor_legint.vendorlist_id = vendorlist.id) \
             ORDER BY lastUpdated" % (purpose_number, purpose_number)
    rows = execute(query, return_rows = True)
    for row in rows:
        counts.append(row[0])
        dates.append(row[1])
    plt.plot(dates, counts)
    plt.xlabel("time")
    plt.ylabel('Nb vendors using purpose %d with leg int' % purpose_number)
    plt.show()

if __name__ == "__main__":
    db = start_db()
    for i in range(1,11):
        compute_evolution(i)
    #compute_evolution(4)
