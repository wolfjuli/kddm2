#!/usr/bin/env python2.7
from string import maketrans, punctuation

from mail_functions import *

import hashlib
import MySQLdb


def mapToSQL(map, tablename):
    map.pop('', None)
    vals = [v.translate(maketrans("", ""), punctuation) for v in map.values()]
    return "insert into " + tablename + '(`' + '`, `'.join(map.keys()) + "`) values ('" + "', '".join(vals) + "'); "


allFiles = getListOfFiles('../maildir')

db = MySQLdb.connect("localhost","kddm2","kddm2","kddm2" )

def flush(cursor):
    cursor.fetchall()
    cursor.close()
    return db.cursor()


cursor = db.cursor()

columnNames = []
cursor.execute("select lower(column_name) from information_schema.columns where table_name = 'mails'")

results = cursor.fetchall()
for cols in results:
    columnNames.append(cols[0])

print "Following columns are already present: "
print columnNames

cursor = db.cursor()


cursor.execute("select filepath from mails")
parsedFiles = {}
for c in cursor.fetchall():
    parsedFiles[c[0]] = 1

count = 0
print str(len(parsedFiles)) + " already parsed files"
for file in allFiles:
    count += 1

    if count % 10000 == 0:
        print "checked " + str(count) + " files"

    if file.translate(maketrans("", ""), punctuation) in parsedFiles:
        #print "skip " + file
        continue

    #print "working on " + file
    parsed = getParsedContent(file)

    for key in [p.lower() for p in parsed.keys() if p.lower() not in columnNames and p != ""]:
        print "adding " + key + " column to database"
        cursor.execute("alter table mails add `" + key + "` longtext")
        columnNames.append(key.lower())

    sql = mapToSQL(parsed, 'mails')
    try:
        cursor.execute(sql)
    except Exception, e:
        print "This mail failed: " + str(e)
        print sql
        cursor.execute("insert into failed (filename, errortext) values ('" + file.translate(maketrans("", ""), punctuation) + "', '" + str(e).translate(maketrans("", ""), punctuation) + "')")
        cursor = flush(cursor)


cursor = flush(cursor)
print "Creating SHA values for paragraphs"
cursor.execute("select id, body from mails")

count = 0
for line in cursor.fetchall():
    count += 1
    paragraphs = line[1].split("\n\n")

    for p in paragraphs:
        cursor.execute("insert into mail_paragraphs (mailId, sha) values (" + str(line[0]) + ", sha('" + p + "'))")
        cursor.execute("insert into sha_paragraphs (sha, paragraph) values ('" + hashlib.sha256(p) + "', '" + p + "')")

    if count % 10000 == 0:
        print str(count) + " mails handled"

    cursor = flush(cursor)
db.close()

