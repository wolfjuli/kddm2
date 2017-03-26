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

print "Creating SHA values for paragraphs"
cursor.execute('select sha from sha_paragraphs')

sha_vals = {}
mail_para = {}
for line in cursor.fetchall():
    sha_vals[line[0]] = 1


print str(len(sha_vals.keys())) + ' sha values already in database'

cursor.execute("select id, body from mails")

count = 0
sumparagraphs = 0
needflush = 0
for line in cursor.fetchall():
    count += 1
    paragraphs = line[1].split("\n\n")

    sumparagraphs += len(paragraphs)
    sortorder = 0
    for p in paragraphs:
        sortorder += 1
        if str(hashlib.sha256(p).hexdigest()) not in sha_vals:
            cursor.execute("insert into sha_paragraphs (sha, paragraph) values ('" + str(hashlib.sha256(p).hexdigest()) + "', '" + p + "')")
            #print "insert into sha_paragraphs (sha, paragraph) values ('" + str(hashlib.sha256(p).hexdigest()) + "', '" + p + "')"
            sha_vals[str(hashlib.sha256(p).hexdigest())] = 1
            needflush = 1


        cursor.execute("update mail_paragraphs set sortorder = " + str(sortorder) + \
                       " where mailId = " + str(line[0]) + " and sha = '" + str(hashlib.sha256(p).hexdigest()) + "'")

        needflush = 1


    if count % 10000 == 0:
        print str(count) + " mails handled (" + str(len(sha_vals.keys())) + " sha values, sum paragraphs: " + \
              str(sumparagraphs) + " = ~" + str(int(len(sha_vals.keys()) / (sumparagraphs + 0.) * 100 + 0.5)) + "%)"

        if needflush == 1:
            cursor = flush(cursor)
            needflush = 0

db.close()

