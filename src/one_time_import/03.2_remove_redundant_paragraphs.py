#!/usr/bin/env python3
import csv
from db_helper import *

db = getDB()
cursor = db.cursor()

cursor.execute('''
SET group_concat_max_len = 18446744073709547520
''')

print("Fetching pairs")
cursor.execute("""
select x.mailId, x.sha, y.mailId, y.sha from
(SELECT mailId, GROUP_CONCAT(pid SEPARATOR '-') as sha, count(*) c
from kddm2.mail_paragraphs
group by mailId
having c > 1) x
join
(SELECT mailId, GROUP_CONCAT(pid SEPARATOR '-') as sha, count(*) c
from kddm2.mail_paragraphs
group by mailId
having c > 1) y
on x.c > y.c
where x.sha like CONCAT('%',y.sha,'%');
""")

print("{} duplicates found".format(cursor.rowcount))
with open("duplicates.csv", "w") as file:
    csvfile = csv.writer(file)

    for row in cursor.fetchall():
        csvfile.writerow(row)
        cursor.execute("update mail_paragraphs set deleted = 1 where mailId = {}".format(row[2]))
        #print("FOUND {:>20} Mail {} with codes {} found in mail {}.".format(c, row[2], row[3], row[0]))

flush(cursor)


