import pymysql
import json
import os

class User:
    is_authenticated = False
    id = None
    first_name = None
    last_name = None
    email = None

    def __init__(self, user_info):
        user_json = json.loads(user_info)
        self.id = user_json['user_id']
        self.first_name = user_json['first_name']
        self.last_name = user_json['last_name']
        self.email = user_json['email']

    def is_active(self):
        return True #all user accounts active for now

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return self.is_authenticated

    def is_anonymous(self):
        return False


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
    def get_users_list(limit, offset, var='*'):
        sql=f"SELECT %s FROM commerce2.users ORDER BY user_id LIMIT %s OFFSET %s;" \
            % (var, limit, offset)
        print(sql)
        conn = UsersResource._get_connection()
        cur = conn.cursor()
        res = cur.execute(sql)
        result = list(cur.fetchall())

        return result

    @staticmethod
    def add_user(uid, first_name, last_name, email, addr_id=None, is_admin="0", is_authenticated="0"):
        print(f"Adding user {uid}: {email}")
        sql = "INSERT INTO commerce2.users (`user_id`, `first_name`, `last_name`, " \
              "`email`, `address_id`, `is_admin`, `is_authenticated`) " \
              "VALUES (%s, %s, %s,%s, %s, %s, %s)"
        conn = UsersResource._get_connection()
        cur = conn.cursor()

        res = cur.execute(sql, (uid, first_name, last_name, email, addr_id, is_admin, is_authenticated))
        result = cur.fetchone()

        return result

    @staticmethod
    def remove_user(uid):
        sql = "DELETE FROM commerce2.users " \
              f"WHERE user_id='{uid}';"
        print(sql)
        conn = UsersResource._get_connection()
        cur = conn.cursor()

        res = cur.execute(sql)

    @staticmethod
    def add_user_from_class(user):
        return UsersResource.add_user(user.id, user.first_name, user.last_name, user.email)

    @staticmethod
    def get_user_by_id(key, var="*"):

        sql = f"SELECT {var} FROM commerce2.users where user_id='{key}'"
        conn = UsersResource._get_connection()
        cur = conn.cursor()
        res = cur.execute(sql)
        result = cur.fetchone()

        return result

    @staticmethod
    def update_db_element(key, param, val):
        sql = f"UPDATE commerce2.users " \
              f"SET {param}='{val}' " \
              f"WHERE user_id='{key}';"
        print(sql)
        conn = UsersResource._get_connection()
        cur = conn.cursor()
        res = cur.execute(sql)
        result = cur.fetchone()

        return result

    @staticmethod
    def get_user_class_by_id(key):
        res = UsersResource.get_user_by_id(key)
        if res is None:
            return None
        user = User(json.dumps(res))
        user.is_authenticated = res['is_authenticated']
        return user

