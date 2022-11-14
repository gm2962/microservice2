import pymysql

import os


class UsersResource:

    def __int__(self):
        pass

    @staticmethod
    def _get_connection():
        usr = os.environ.get("DBUSER")
        pw = os.environ.get("DBPW")
        h = os.environ.get("DBHOST")

        conn = pymysql.connect(
            user=usr,
            password=pw,
            host=h,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )

        return conn


    @staticmethod
    def get_users_list(limit, offset):
        sql="SELECT * FROM commerce2.users ORDER BY user_id LIMIT %s OFFSET %s;" % (limit, offset)
        print(sql)
        conn = UsersResource._get_connection()
        cur = conn.cursor()
        res = cur.execute(sql)
        result = list(cur.fetchall())

        return result

    @staticmethod
    def add_user(uid, first_name, last_name, email):
        sql = "INSERT INTO commerce2.users (`user_id`, `first_name`, `last_name`, `email`) VALUES (%s, %s, %s,%s)"
        conn = UsersResource._get_connection()
        cur = conn.cursor()

        res = cur.execute(sql, (uid, first_name, last_name, email))
        result = cur.fetchone()

        return result

    @staticmethod
    def get_user_by_id(key, var="*"):

        sql = "SELECT " + var + " FROM commerce2.users where user_id=%s"
        conn = UsersResource._get_connection()
        cur = conn.cursor()
        res = cur.execute(sql, args=key)
        result = cur.fetchone()

        return result

