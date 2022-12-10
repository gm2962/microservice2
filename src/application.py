from flask import Flask, Response, request, redirect, session
import json
import random
import os
from flask.templating import render_template
from flask import redirect
from users import UsersResource
from cards import CardResource
from address import AddrResource
from microservice2.middleware.notification import SNSHandler
from microservice2.middleware.login import loginHandler
from flask_cors import CORS


# Create the Flask application object.
app = Flask(__name__)

CORS(app)
loginHandler.init_oauth(app)

#SNS locations relevent to this microservice
WELCOME_EMAIL_SNS = 'arn:aws:sns:us-east-1:220478294544:welcome-email'


#login setup
app.secret_key = "3487836939993559999334502"

IGNORE_LOGIN_ENDPOINTS =['login_callback', 'is_admin']


@app.route('/login_callback')
def login_callback():
    resp = loginHandler.login_cb()
    user_info = resp.json()
    print(" Google User ", user_info)
    session["user_info"] = user_info
    return redirect('/')


@app.route('/login')
def login_fnc():
    if 'user_info' not in session:
        return loginHandler.call_to_login('login_callback')
    else:
        email = dict(session)['user_info']['email']
        return f"Welcome {email}"

@app.before_request
def check_login():
    not_login_cb = False
    if request.endpoint is None:
        not_login_cb = True
    elif request.endpoint not in IGNORE_LOGIN_ENDPOINTS:
        not_login_cb = True

    if not_login_cb and 'user_info' not in session:
        return loginHandler.call_to_login('login_callback')

@app.after_request
def trigger_event(response):
    if request.path == '/add_user' and request.method == 'POST':
        message = {"admin_email": "test@columbia.edu"}
        SNSHandler.send_sns_message(
            WELCOME_EMAIL_SNS,
            message
        )
    return response

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return "You are logged out"

@app.route("/")
def landing_page():
    email = dict(session)['user_info']['email']
    return f'Hello, you are logged in as {email}!'

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

@app.route("/is_admin", methods=["GET"])
def is_admin():
    data = request.json
    result = UsersResource.get_user_by_id(data["user_id"])

    return_data = {"is_admin": 0}
    if result:
        return_data["is_admin"] = 1
    return Response(json.dumps(return_data), status=200, content_type="text/plain")

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

