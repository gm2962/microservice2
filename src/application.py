from flask import Flask, Response, request, redirect, session
import json
import random
import os
from flask.templating import render_template
from flask import redirect
from users import User
from users import UsersResource
from cards import CardResource
from address import AddrResource
from notification import SNSHandler
from login import loginHandler
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


    #check if in db
    result = UsersResource.get_user_by_id(user_info["id"])
    if result is None:
        #create the account then update it
        user_data = {
            "user_id":user_info["id"],
            "first_name":user_info["given_name"],
            "last_name":user_info["family_name"],
            "email":user_info["email"]
        }

        user = User(json.dumps(user_data))
        UsersResource.add_user_from_class(user)
        loginHandler.login_current_user(user)
        return redirect("/welcome")

    user = User(json.dumps(result))
    loginHandler.login_current_user(user)
    return redirect('/')


@app.route('/login')
def login_fnc():
    if 'user_info' not in session:
        return loginHandler.call_to_login()
    else:
        email = dict(session)['user_info']['email']
        return f"Welcome {email}"

@app.before_request
def check_login():
    require_login = False
    if request.endpoint is None:
        require_login = True
    elif request.endpoint not in IGNORE_LOGIN_ENDPOINTS:
        require_login = True

    if require_login:
        if not loginHandler.is_verified(): #not logged in
            return loginHandler.call_to_login()

@app.after_request
def trigger_event(response):
    if request.path == '/welcome':
        user_info = json.loads(loginHandler.load_user_data())
        send_to = user_info['email']
        print(f"Sending welcome email to {send_to}")
        message = {"send_email": send_to}
        SNSHandler.send_sns_message(
            WELCOME_EMAIL_SNS,
            message
        )
    return response

@app.route('/logout')
def logout():
    loginHandler.logout()
    return "You are logged out"

@app.route("/")
@app.route("/welcome")
def landing_page():
    user = json.loads(loginHandler.load_user_data())
    email = user["email"]
    first_name = user["first_name"]
    last_name = user["last_name"]
    return f'Hello {first_name} {last_name}! You are logged as {email}!'

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

@app.route("/update_account", methods=["GET", "POST"])
def update_account():
    user_id = loginHandler.get_user_id()
    email = UsersResource.get_user_by_id(user_id, var="email")
    if email is None:
        redirect("/login")

    if request.method == "GET":
        return render_template("create_account.html", email=email)

    add_admin = '0'
    if 'is_admin' in request.form:
        add_admin = '1'

    number = request.form.get("number")
    street = request.form.get("street")
    city = request.form.get("city")
    state = request.form.get("state")
    zipcode = request.form.get("zip")

    if not AddrResource.verify_address(number + " " + street, zipcode, state, city):
        return Response("ADDRESS INVALID: update account failed...please try again", status=404, content_type="text/plain")

    #check if address is already associated with this user
    maybe_addr = UsersResource.get_user_by_id(user_id, "address_id")
    add_address = False
    if maybe_addr is None:
        add_address = True
    elif maybe_addr["address_id"] is None:
        add_address = True

    if add_address:
        addr_id = "addr" + str(random.randint(0, 1024))
        AddrResource.add_address(addr_id, number, street, city, state, zipcode)
        UsersResource.update_db_element(user_id, "`address_id`", addr_id)
    else:
        AddrResource.update_address(maybe_addr["address_id"], number, street, city, state, zipcode)

    UsersResource.update_db_element(user_id, "is_admin", add_admin)
    return redirect(f"/users/{user_id}")

@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    #check if admin is adding another user
    admin_id = loginHandler.get_user_id()
    result = UsersResource.get_user_by_id(admin_id, var="is_admin")
    if result is None:
        #user not in database. redirect to create account
        return redirect("/create_account")
    if result["is_admin"] == 0:
        return Response("Current user unauthorized to add user", status=401, content_type="text/plain")


    if request.method == 'POST':
        user_id = "user" + str(random.randint(0, 1024))
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        add_admin = '0'
        if request.form.get('is_admin') == "on":
            add_admin = '1'

        addr_id = "addr" + str(random.randint(0, 1024))
        number = request.form.get("number")
        street = request.form.get("street")
        city = request.form.get("city")
        state = request.form.get("state")
        zipcode = request.form.get("zip")

        if not AddrResource.verify_address(number + " " + street, zipcode, state, city):
            return Response("ADDRESS INVALID", status=404, content_type="text/plain")

        AddrResource.add_address(addr_id, number, street, city, state, zipcode)
        UsersResource.add_user(user_id, first_name, last_name, email, addr_id, add_admin)

        return redirect("/users/" + user_id)
    return render_template('add_user.html')

@app.route("/delete_account", methods=["GET"])
def delete_my_account():
    user_id = loginHandler.get_user_id()
    loginHandler.logout()
    UsersResource.remove_user(user_id)
    return f"Removed user with id {user_id}"

@app.route("/is_admin", methods=["GET"])
def is_admin():
    data = request.json
    result = UsersResource.get_user_by_id(data["user_id"], var="is_admin")

    return_data = {"is_admin": 0}
    if result:
        return_data["is_admin"] = result["is_admin"]
    return Response(json.dumps(return_data), status=200, content_type="text/plain")

@app.route("/delete_my_account")
def delete_account():
    pass

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

