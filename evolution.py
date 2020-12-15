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

def compute_evolution(purpose_number, relative=False):
    counts = []
    dates = []
    total_counts = []
    relative_counts = []
    query = "SELECT COUNT(*), lastUpdated FROM vendor_legint LEFT JOIN vendorlist ON vendor_legint.vendorlist_id = vendorlist.id WHERE legint = %d GROUP BY vendorlist_id \
             UNION SELECT 0, lastUpdated FROM vendorlist WHERE id NOT IN (SELECT vendorlist_id FROM vendor_legint WHERE legint = %d AND vendor_legint.vendorlist_id = vendorlist.id) \
             ORDER BY lastUpdated" % (purpose_number, purpose_number)
    rows = execute(query, return_rows = True)
    for row in rows:
        counts.append(row[0])
        dates.append(row[1])
    if relative:
        query = "SELECT COUNT(*), vendorlist_id FROM vendor GROUP BY vendorlist_id \
                 UNION SELECT 0, id FROM vendorlist WHERE id NOT IN (SELECT vendorlist_id FROM vendor WHERE vendor.vendorlist_id = vendorlist.id) \
                 ORDER BY vendorlist_id"
        rows = execute(query, return_rows = True)
        for row in rows:
            total_counts.append(row[0])
        for vendorlist_id in range(0, len(counts)):
            if total_counts[vendorlist_id] > 0:
                relative_counts.append(counts[vendorlist_id]/total_counts[vendorlist_id])
            else:
                relative_counts.append(0)
        plt.plot(dates, relative_counts)
        plt.ylabel('Proportion of vendors using purpose %d with leg int' % purpose_number)
    else:
        plt.plot(dates, counts)
        plt.ylabel('Nb vendors using purpose %d with leg int' % purpose_number)
    plt.xlabel("time")
    plt.show()

if __name__ == "__main__":
    db = start_db()
    for i in range(1,11):
        compute_evolution(i, relative=True)
    #compute_evolution(4, relative=True)
