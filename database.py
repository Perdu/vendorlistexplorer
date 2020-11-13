#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import datetime
import configparser

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, BigInteger
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import LargeBinary
import MySQLdb as mdb

from utils import *

Base = declarative_base()

def start_db_orm():
    config = parse_config_file(CONFIG_FILE)
    eng = create_engine('mysql://' + config.db_user + ':' +
                        config.db_pass + '@' + config.db_server +
                        '/' + config.db_name, pool_recycle=3600)
    Base.metadata.bind = eng
    Session = sessionmaker(bind=eng)
    db = Session()
    Base.metadata.create_all(bind=eng)
    return db

def start_db():
    config = parse_config_file(CONFIG_FILE) # todo: we shouldn't parse file on each request
    return mdb.connect(config.db_server, config.db_user, config.db_pass, config.db_name)

########### CLASSES
class Vendorlist(Base):
    __tablename__ = "vendorlist"
    id = Column(Integer, primary_key=True)
    lastUpdated = Column(DateTime)
    def __init__(self, vendorlist_id):
        self.id = vendorlist_id

class Vendor(Base):
    __tablename__ = "vendor"
    id = Column(Integer, primary_key=True)
    vendorlist_id = Column(Integer, ForeignKey("vendorlist.id"), primary_key=True)
    name = Column(String(256))
    url = Column(String(1200)) # max length on IAB's registration form
    cookieMaxAgeSeconds = Column(BigInteger)
    usesNonCookieAccess = Column(Integer)
    def __init__(self, vendor_id, vendorlist_id):
        self.id = vendor_id
        self.vendorlist_id = vendorlist_id

class Vendor_purpose(Base):
    __tablename__ = "vendor_purpose"
    vendor_id = Column(Integer, ForeignKey("vendor.id"), primary_key=True)
    vendorlist_id = Column(Integer, ForeignKey("vendorlist.id"), primary_key=True)
    purpose = Column(Integer, primary_key=True)
    def __init__(self, vendor_id, vendorlist_id, purpose):
        self.vendor_id = vendor_id
        self.vendorlist_id = vendorlist_id
        self.purpose = int(purpose)

class Vendor_legint(Base):
    __tablename__ = "vendor_legint"
    vendor_id = Column(Integer, ForeignKey("vendor.id"), primary_key=True)
    vendorlist_id = Column(Integer, ForeignKey("vendorlist.id"), primary_key=True)
    legint = Column(Integer, primary_key=True)
    def __init__(self, vendor_id, vendorlist_id, legint):
        self.vendor_id = vendor_id
        self.vendorlist_id = vendorlist_id
        self.legint = legint

class Vendor_flexible_purpose(Base):
    __tablename__ = "vendor_flexible_purpose"
    vendor_id = Column(Integer, ForeignKey("vendor.id"), primary_key=True)
    vendorlist_id = Column(Integer, ForeignKey("vendorlist.id"), primary_key=True)
    flexible_purpose = Column(Integer, primary_key=True)
    def __init__(self, vendor_id, vendorlist_id, flexible_purpose):
        self.vendor_id = vendor_id
        self.vendorlist_id = vendorlist_id
        self.flexible_purpose = flexible_purpose

class Vendor_special_purpose(Base):
    __tablename__ = "vendor_special_purpose"
    vendor_id = Column(Integer, ForeignKey("vendor.id"), primary_key=True)
    vendorlist_id = Column(Integer, ForeignKey("vendorlist.id"), primary_key=True)
    special_purpose = Column(Integer, primary_key=True)
    def __init__(self, vendor_id, vendorlist_id, special_purpose):
        self.vendor_id = vendor_id
        self.vendorlist_id = vendorlist_id
        self.special_purpose = special_purpose

class Vendor_feature(Base):
    __tablename__ = "vendor_feature"
    vendor_id = Column(Integer, ForeignKey("vendor.id"), primary_key=True)
    vendorlist_id = Column(Integer, ForeignKey("vendorlist.id"), primary_key=True)
    feature = Column(Integer, primary_key=True)
    def __init__(self, vendor_id, vendorlist_id, feature):
        self.vendor_id = vendor_id
        self.vendorlist_id = vendorlist_id
        self.feature = feature

class Vendor_special_feature(Base):
    __tablename__ = "vendor_special_feature"
    vendor_id = Column(Integer, ForeignKey("vendor.id"), primary_key=True)
    vendorlist_id = Column(Integer, ForeignKey("vendorlist.id"), primary_key=True)
    special_feature = Column(Integer, primary_key=True)
    def __init__(self, vendor_id, vendorlist_id, special_feature):
        self.vendor_id = vendor_id
        self.vendorlist_id = vendorlist_id
        self.special_feature = special_feature

########### FUNCTIONS
def parse_config_file(config_file):
    c = configparser.RawConfigParser()
    if not c.read(config_file):
        print("Could not find config file %s." % config_file)
        print('Please copy it from %s.example and fill it appropiately.' % CONFIG_FILE)
        sys.exit(1)
    config = Config(c)
    return config
