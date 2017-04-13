def getDB():
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

    return db

def flush(cursor):
    global db
    db.commit()
    cursor.fetchall()
    cursor.close()
    return db.cursor()