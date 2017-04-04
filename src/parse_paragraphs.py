#!/bin/env python2.7

import MySQLdb
import hashlib

db = MySQLdb.connect("localhost","kddm2","kddm2","kddm2" )
cursor = db.cursor()



def flush(cursor):
    cursor.fetchall()
    cursor.close()
    return db.cursor()

print "Creating SHA values for paragraphs"
cursor.execute("select id, body from mails")

count = 0
for line in cursor.fetchall():
    count += 1
    paragraphs = line[1].split("\n\n")

    for p in paragraphs:
        cursor.execute("insert into mail_paragraphs (mailId, sha) values (" + str(line[0]) + ", '" + hashlib.sha256(p) + "')")
        cursor.execute("insert into sha_paragraphs (sha, paragraph) values ('" + hashlib.sha256(p) + "', '" + p + "')")

    if count % 10000 == 0:
        print str(count) + " mails handled"

    cursor = flush(cursor)