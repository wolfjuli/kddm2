#!/usr/bin/env python3
from string import punctuation
from hashlib import sha256
from mail_functions import *
from DBHelper import DBHelper


def mapToSQL(map, tablename):
    imp = map.copy()
    imp.pop('', None)
    imp.pop('body', None)
    imp.pop('SHABody', None)
    vals = [str(v).replace("'", "") for v in imp.values()]
    return "insert into " + tablename + '(`' + '`, `'.join(imp.keys()) + "`) values ('" + "', '".join(vals) + "'); "

db = DBHelper()

columnNames = [cols[0] for cols in db.execute("select lower(column_name) from information_schema.columns where table_name = 'mails'")]
print("Following columns are already present: \n {}".format(columnNames))

sha_vals = {line[0]: line[1] for line in db.execute("select sha, id from sha_paragraphs")}
print(str(len(sha_vals)) + ' sha values already in database')

parsedFiles = {c[0].strip(): 1 for c in db.execute("select filepath from mails")}

count = 0
sumparagraphs = 0
sumdistinctparagraphs = len(sha_vals)
print(str(len(parsedFiles)) + " already parsed files")

for file in getListOfFiles('../../maildir'):
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
    try:
        db.execute(mapToSQL(parsed, 'mails'), True)
    except Exception as e:
        db.execute("insert into failed (filename, errortext) values ('{}','{}')"
                   .format(strip(file, punctuation), strip(str(e), punctuation)))

    for t in parsed['To'].split(","):
        db.execute("insert into from_to_mail (`from`, `to`, mailId) values ('{}','{}',{})"
                   .format(parsed['From'].replace("'", ""), t.strip().replace("'", ""), parsed['id']))

    paragraphs = strip(parsed['body'], punctuation).split("\n\n")
    sortorder = 0

    for p in [p.strip() for p in paragraphs if p.strip() != ""]:
        sortorder += 1
        sumparagraphs += 1
        hash = str(sha256(p.encode('UTF-8')).hexdigest())
        if hash not in sha_vals:
            sumdistinctparagraphs += 1
            db.execute("insert into sha_paragraphs (sha, paragraph, id) values ('{}', '{}', {})"
                           .format(hash, p, sumdistinctparagraphs))
            sha_vals[hash] = sumdistinctparagraphs

        db.execute("insert into mail_paragraphs (mailId, sha, sortorder, pid) values ({}, '{}', {}, {})"
                       .format(str(parsed['id']), hash, sortorder, sha_vals[hash]))

    if count % 10000 == 0:
        print("{} files checked. sum paragraphs: {}, distinct paragraphs: {} = ~{}%)"
              .format(count, sumparagraphs, len(sha_vals), int(len(sha_vals) / (sumparagraphs + 0.) * 100 + 0.5)))
        db.flush()

db.flush()
