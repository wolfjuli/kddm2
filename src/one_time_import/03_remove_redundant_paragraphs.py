#!/usr/bin/env python3
from db_helper import *

db = getDB()
cursor = db.cursor()

cursor.execute('''
SET group_concat_max_len = 18446744073709547520
''')

print("Fetching all mails")
cursor.execute("""
SELECT mailId, GROUP_CONCAT(pid SEPARATOR '-') as sha, count(*)
from mail_paragraphs
group by mailId;
""")

print("building set")
allMails = {}
mailCount = {}
oldMailId = ""
for mail_para in cursor.fetchall():
    if mail_para[0] not in allMails:
        allMails[mail_para[0]] = []

    #create count set
    if oldMailId != mail_para:
        if oldMailId != "":
            count = len(allMails[oldMailId])
            if count not in mailCount:
                mailCount[count] = []
            mailCount[count].append(oldMailId)

        oldMailId = mail_para[0]

    allMails[mail_para[0]].append(mail_para[1])

cursor = flush(cursor)
for i in mailCount.keys():
    #run through all mails in this paragraph count list
    for smallMailId in mailCount[i]:
        #check with all other mails which have more paragraphs
        for j in [k for k in mailCount.keys() if k > i]:
            for largeMailId in mailCount[j]:
                if set(allMails[smallMailId]).issubset(allMails[largeMailId]):
                    #the smaller mail was a subset of the bigger mail - delete it from the bigger mail
                    for sha in allMails[smallMailId]:
                        cursor.execute("""update mail_paragraphs set deleted = 1 where mailId = %s and sha = %s""", (largeMailId, sha))

                    cursor = flush(cursor)
                    print("Mail {} was in mail {}".format(smallMailId, largeMailId))


