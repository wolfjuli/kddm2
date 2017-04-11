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
    cursor.execute("alter table mail_paragraphs add deleted int")
    cursor = flush(cursor)

cursor.execute("""
select count(*) c, mailId
from mail_paragraphs
group BY mailId
order by c, mailId
""")




