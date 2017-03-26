#!/usr/bin/env python2.7
from string import maketrans, punctuation

from src.mail_functions import *

import hashlib
import MySQLdb


db = MySQLdb.connect("localhost","kddm2","kddm2","kddm2" )

def flush(cursor):
    db.commit()
    cursor.fetchall()
    cursor.close()
    return db.cursor()


cursor = db.cursor()

names = {}
from_to_mails = {}
cursor.execute("select n.name from names n")
for line in cursor.fetchall():
    names[line[0]] = 1

count = 0
needFlush = 0
cursor.execute("select m.`from`, m.`to`, m.`x-from`, m.`x-to` from mails m")
for line in cursor.fetchall():
    words = line[0].split(' ') + line[1].split(' ')

    for name in [w.translate(maketrans("", ""), "\t\n\r") for w in words if w not in names]:
        cursor.execute("insert into names (name) values ('" + name + "')")
        needFlush = 1
        names[name] = 1




    if count % 1000 == 0:
        print "processed 1000 mails, " + str(len(names.keys())) + ' distinct names found'
