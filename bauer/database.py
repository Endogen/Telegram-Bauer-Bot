import os
import sqlite3
import inspect
import bauer.emoji as emo
import bauer.constants as c


class Database:

    # Initialize database
    def __init__(self, db_path="data.db"):
        self._db_path = db_path

        # Create 'data' directory if not present
        data_dir = os.path.dirname(db_path)
        os.makedirs(data_dir, exist_ok=True)

        con = sqlite3.connect(db_path)
        cur = con.cursor()

        # If tables don't exist, create them
        if not cur.execute(self.get_sql("db_exists")).fetchone():
            # TODO: Which tables are needed?
            # cur.execute(self.get_sql("users"))
            # con.commit()

            con.close()

        # TODO: Which statements do we need?
        # self.usr_exist_sql = self.get_sql("user_exists")

    # Get string with SQL statement from file
    def get_sql(self, filename):
        cls = inspect.stack()[1][0].f_locals["self"].__class__
        cls_name = cls.__name__.lower()
        filename = f"{filename}.sql"

        with open(os.path.join(c.SQL_DIR, cls_name, filename)) as f:
            return f.read()

    # Execute raw SQL statements on database
    def execute_sql(self, sql, *args):
        dic = {"result": None, "error": None}

        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        try:
            cur.execute(sql, args)
            con.commit()
            dic["result"] = cur.fetchall()
        except Exception as e:
            dic["error"] = f"{emo.ERROR} {e}"

        con.close()
        return dic
