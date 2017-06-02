class DBHelper:
    def __init__(self):
        self.cursor = self._get_cursor()
        self.rowcount = 0

    @staticmethod
    def _get_cursor():
        try:
            import MySQLdb
            db = MySQLdb.connect("localhost","kddm2","kddm2","kddm2")
        except:
            try:
                import pymysql
                db = pymysql.connect("localhost","kddm2","kddm2","kddm2")
            except:
                import pymssql
                db = pymssql.connect("localhost", "kddm2", "kddm2", "kddm2")

        return db.cursor()

    def flush(self):
        self.cursor.connection.commit()
        new_cursor = self.cursor.connection.cursor()
        self.cursor.close()
        self.cursor = new_cursor

    def execute(self, sql, commit=False):
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            self.rowcount = self.cursor.rowcount
            if commit:
                self.flush()

        except Exception as e:
            results = None
            self.rowcount = 0
            print("Error executing script: '{}' because '{}'".format(sql, str(e)))

        return results

