#!/usr/bin/env python3


try:
    import MySQLdb
    db = MySQLdb.connect("localhost","kddm2","kddm2","kddm2" )
except:
    try:
        import pymysql
        db = pymysql.connect("localhost","kddm2","kddm2","kddm2" )
    except:
        import pymssql
        db = pymssql.connect("localhost", "kddm2", "kddm2", "kddm2")

def flush(cursor):
    db.commit()
    cursor.fetchall()
    cursor.close()
    return db.cursor()


cursor = db.cursor()

#check if column exists
cursor.execute("""
select column_name
from information_schema.COLUMNS
where TABLE_NAME = 'mail_paragraphs'
and column_name = 'deleted'
""")

if len(cursor.fetchall()) == 0:
    print("Table does not have the deleted column - creating it. This takes log - go fetch a coffee")
    cursor.execute("alter table mail_paragraphs add deleted int DEFAULT 0")
    cursor = flush(cursor)

print("Fetching all mails")
cursor.execute("""
select mailid, sha
from mail_paragraphs
where deleted = 0
order by mailid, sortorder
""")


print("building set")
allMails = {}
mailCount = {}
oldMailId = ""
for mail_para in cursor.fetchall():
    if mail_para[0] not in allMails:
        allMails[mail_para[0]] = []

    #create count set
    if oldMailId != mail_para and oldMailId != "":
        count = len(allMails[oldMailId])
        if count not in mailCount:
            mailCount[count] = []

        mailCount[count] += oldMailId
        oldMailId = mail_para[0]

    allMails[mail_para[0]] += mail_para[1]


cursor = flush(cursor)
for i in range(1, max(mailCount)):
    #run through all mails in this paragraph count list
    for smallMailId in mailCount[i]:
        #check with all other mails which have more paragraphs
        for j in range(i + 1, max(mailCount)):
            for largeMailId in mailCount[j]:
                if set(allMails[smallMailId]).issubset(allMails[largeMailId]):
                    #the smaller mail was a subset of the bigger mail - delete it from the bigger mail
                    for sha in allMails[smallMailId]:
                        cursor.execute("""update mail_paragraphs set deleted = 1 where mailId = %s and sha = %s""", (largeMailId, sha))

                    cursor = flush(cursor)
                    print("Mail %s was in mail %s", (smallMailId, largeMailId))


