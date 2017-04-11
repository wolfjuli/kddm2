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

count = 0
needFlush = 0
cursor.execute("select m.`from`, m.`to`, m.`x-from`, m.`x-to`, m.id from mails m")
for line in cursor.fetchall():

    count += 1
    for t in str(line[1]).split(","):
        cursor.execute("insert into from_to_mail (`from`, `to`, mailId) values (%s, %s, %s)", (line[0], str(t).strip(), line[4]))

    cursor = flush(cursor)

    if count % 1000 == 0:
        print "processed " + str(count) + " mails"
