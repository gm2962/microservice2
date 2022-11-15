from flask import Flask, Response, request
from datetime import datetime
import json
import random
from flask.templating import render_template
from flask import redirect
from users import UsersResource
from cards import CardResource
from address import AddrResource
from flask_cors import CORS


# Create the Flask application object.
app = Flask(__name__)

CORS(app)

@app.route("/users", methods=["GET"])
def get_users():
    limit = request.args.get("limit", default=5)
    offset = request.args.get("offset", default=0)

    results = UsersResource.get_users_list(limit, offset)
    if results:
        rsp = Response(json.dumps(results), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")

    return rsp


@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    if request.method == 'POST':
        user_id = "user" + str(random.randint(0, 1024))
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')

        addr_id = "addr" + str(random.randint(0, 1024))
        number = request.form.get("number")
        street = request.form.get("street")
        city = request.form.get("city")
        state = request.form.get("state")
        zipcode = request.form.get("zip")

        if not AddrResource.verify_address(number + " " + street, zipcode, state, city):
            return Response("ADDRESS INVALID", status=404, content_type="text/plain")

        AddrResource.add_address(addr_id, number, street, city, state, zipcode)
        UsersResource.add_user(user_id, first_name, last_name, email, addr_id)

        return redirect("/users/" + user_id)
    return render_template('add_user.html')


@app.route("/users/<user_id>", methods=["GET"])
def get_user_by_id(user_id):
    result = UsersResource.get_user_by_id(user_id)

    if result:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")

    return rsp


@app.route("/users/<user_id>/cards", methods=["GET"])
def get_cid_from_user_id(user_id):
    result = UsersResource.get_user_by_id(user_id, "credit_id")

    if result:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")

    return rsp

@app.route("/users/<user_id>/cards/<cid>", methods=["GET"])
def get_card_id(user_id, cid):
    result = CardResource.get_card_by_id(cid)

    if result:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")

    return rsp


@app.route("/users/<user_id>/addresses", methods=["GET"])
def get_addr_from_user_id(user_id):
    result = UsersResource.get_user_by_id(user_id, "address_id")

    if result:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")

    return rsp

@app.route("/users/<user_id>/addresses/<aid>", methods=["GET"])
def get_addr_id(user_id, aid):
    result = AddrResource.get_address_by_id(aid)

    if result:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")

    return rsp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5011)

