import os
import sqlite3
import inspect
import logging
import bauer.constants as c


class Database:

    def __init__(self, db_path="data.db"):
        self._db_path = db_path

        # Create 'data' directory if not present
        data_dir = os.path.dirname(db_path)
        os.makedirs(data_dir, exist_ok=True)

        # Open connection to database
        con = sqlite3.connect(db_path)
        cur = con.cursor()

        # If needed tables don't exist, create them
        if not cur.execute(self.get_sql("db_exists")).fetchone():
            cur.execute(self.get_sql("create_users"))
            con.commit()

        con.close()

    def get_sql(self, filename):
        """ Return SQL statement from file """
        cls = inspect.stack()[1][0].f_locals["self"].__class__
        cls_name = cls.__name__.lower()
        filename = f"{filename}.sql"

        with open(os.path.join(c.SQL_DIR, cls_name, filename)) as f:
            return f.read()

    def execute_sql(self, sql, *args):
        """ Execute raw SQL statement on database """
        res = {"success": None, "data": None}
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        try:
            cur.execute(sql, args)
            con.commit()
            res["data"] = cur.fetchall()
            res["success"] = True
        except Exception as e:
            logging.error(e)
            res["data"] = str(e)
            res["success"] = False

        con.close()
        return res

    def table_exists(self, table_name):
        """ Return TRUE if table exists, otherwise FALSE """
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()
        exists = False

        try:
            statement = self.get_sql("table_exists")
            if cur.execute(statement, [table_name]).fetchone():
                exists = True
        except Exception as e:
            logging.error(e)

        con.close()
        return exists

    def save_user(self, user):
        """ Save user details in database """
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        try:
            # Check if user already exists
            statement = self.get_sql("user_exists")
            cur.execute(statement, [user["id"]])
            con.commit()

            # Add user if he doesn't exist
            if cur.fetchone()[0] != 1:
                user_data = [
                    user["id"],
                    user["username"],
                    user["first_name"],
                    user["last_name"],
                    user["language_code"]
                ]

                statement = self.get_sql("add_user")
                cur.execute(statement, user_data)
                con.commit()
        except Exception as e:
            logging.error(e)

        con.close()
