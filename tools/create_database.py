#!/usr/bin/env python2.7
from string import maketrans, punctuation

from mail_functions import *

import os
import cPickle
import time
import MySQLdb


def mapToSQL(map, tablename):
    map.pop('', None)
    vals = [v.translate(maketrans("", ""), punctuation) for v in map.values()]
    return "insert into " + tablename + '(`' + '`, `'.join(map.keys()) + "`) values ('" + "', '".join(vals) + "'); "


allFiles = getListOfFiles('../maildir')

db = MySQLdb.connect("localhost","kddm2","kddm2","kddm2" )

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
        cursor.close()
        cursor = db.cursor()




db.close()