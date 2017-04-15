def getCursor():
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

    return db.cursor()


def flush(cursor):
    cursor.connection.commit()
    newCursor = cursor.connection.cursor()
    cursor.close()
    return newCursor


def execute(cursor, sql, commit=False):
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        c = cursor.rowcount
    except:
        results = None
        c = 0
        print("Error executing script: '{}'".format(sql))
    if commit:
        cursor.connection.commit()
        newCursor = cursor.connection.cursor()
        cursor.close()
        cursor = newCursor
    return cursor, results, c
