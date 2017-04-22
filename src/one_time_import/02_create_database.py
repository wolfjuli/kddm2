#!/usr/bin/env python3
from string import punctuation
import hashlib

from mail_functions import *
from db_helper import *


allFiles = getListOfFiles('../maildir')


def mapToSQL(map, tablename):
    imp = map.copy()
    imp.pop('', None)
    imp.pop('body', None)
    vals = [str(v).replace("'", "") for v in imp.values()]
    return "insert into " + tablename + '(`' + '`, `'.join(imp.keys()) + "`) values ('" + "', '".join(vals) + "'); "

cursor = getCursor()
cursor, results, _ = execute(cursor, "select lower(column_name) from information_schema.columns where table_name = 'mails'")

columnNames = []
for cols in results:
    columnNames.append(cols[0])

print("Following columns are already present: ")
print(columnNames)

cursor, results, _ = execute(cursor, 'select sha, id from sha_paragraphs')

sha_vals = {}
for line in results:
    sha_vals[line[0]] = line[1]

print(str(len(sha_vals.keys())) + ' sha values already in database')

cursor, results, _ = execute(cursor, "select filepath from mails")
parsedFiles = {}
for c in results:
    parsedFiles[c[0].strip()] = 1

count = 0
sumparagraphs = 0
sumdistinctparagraphs = len(sha_vals.keys())
print(str(len(parsedFiles)) + " already parsed files")

allFiles = getListOfFiles('../../maildir')

for file in allFiles:
    count += 1

    if file in parsedFiles:
        continue

    try:
        parsed = getParsedContent(file)
    except:
        continue

    if 'To' not in parsed:
        parsed['To'] = ''

    parsed['id'] = count
    parsedFiles[file] = 1
    sql = mapToSQL(parsed, 'mails')

    try:
        cursor, _, _ = execute(cursor, sql, True)
    except Exception as e:
        print("This mail failed: " + str(e))
        print(sql)
        execute(cursor,
                """insert into failed (filename, errortext)
                           values ('" + stripChars(file, punctuation) + "', '" + stripChars(str(e), punctuation) + "')"""
                )

    for t in parsed['To'].split(","):
        try:
            sql = """insert into from_to_mail (`from`, `to`, mailId) values ('{}','{}',{})""".format(parsed['From'].replace("'", ""), t.strip().replace("'", ""), parsed['id'])
            execute(cursor, sql)
        except Exception as e:
            print("something went wrong with this statement:")
            print(sql)

    paragraphs = stripChars(parsed['body'], punctuation).split("\n\n")
    sortorder = 0

    for p in [p.strip() for p in paragraphs if p.strip() != ""]:
        sortorder += 1
        sumparagraphs += 1
        hash = str(hashlib.sha256(p.encode('UTF-8')).hexdigest())
        if hash not in sha_vals:
            sumdistinctparagraphs +=1
            execute(cursor, """insert into sha_paragraphs (sha, paragraph, id) values ('{}', '{}', {})"""
                           .format(hash, p, sumdistinctparagraphs))
            sha_vals[hash] = sumdistinctparagraphs

        execute(cursor, """insert into mail_paragraphs (mailId, sha, sortorder, pid) values ({}, '{}', {}, {})"""
                       .format(str(parsed['id']), hash, sortorder, sha_vals[hash]))

    if count % 10000 == 0:
        print("checked " + str(count) + " files")
        print("sum paragraphs: " + str(sumparagraphs) + ", distinct paragraphs: " + str(len(sha_vals.keys())) +
              " = ~" + str(int(len(sha_vals.keys()) / (sumparagraphs + 0.) * 100 + 0.5)) + "%)")

        cursor = flush(cursor)

flush(cursor)
