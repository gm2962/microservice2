import pymysql
import os

from smartystreets_python_sdk import StaticCredentials, exceptions, ClientBuilder
from smartystreets_python_sdk.us_street import Lookup as StreetLookup

class AddrResource:
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
    def get_address_by_id(key):
        sql = "SELECT * FROM commerce2.addresses where addr_id=%s"
        conn = AddrResource._get_connection()
        cur = conn.cursor()
        res = cur.execute(sql, args=key)
        result = cur.fetchone()

        return result

    @staticmethod
    def verify_address(street, zip, state, city):
        # auth_id = "Your SmartyStreets Auth ID here"
        # auth_token = "Your SmartyStreets Auth Token here"
        auth_id = os.environ.get('SMARTY_AUTH_ID')
        auth_token = os.environ.get('SMARTY_AUTH_TOKEN')

        credentials = StaticCredentials(auth_id, auth_token)

        client = ClientBuilder(credentials).with_licenses(["us-core-cloud"]).build_us_street_api_client()

        lookup = StreetLookup()
        lookup.street = street
        lookup.city = city
        lookup.zip = zip
        lookup.state = state
        lookup.candidates = 3
        lookup.match = "strict"

        try:
            client.send_lookup(lookup)
        except exceptions.SmartyException as err:
            print(err)
            return False

        result = lookup.result

        if not result:
            print("Address invalid.")
            return False
        return True
    @staticmethod
    def add_address(addr_id, number, street, city, state, zipcode):
        sql = "INSERT INTO commerce2.addresses (`addr_id`, `number`, `street`, `city`, `state`, `zip`) VALUES (%s, %s, %s,%s, %s, %s)"
        conn = AddrResource._get_connection()
        cur = conn.cursor()

        res = cur.execute(sql, (addr_id, number, street, city, state, zipcode))
        result = cur.fetchone()

        return result
