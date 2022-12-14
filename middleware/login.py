from authlib.integrations.flask_client import OAuth
import os
import json
from flask import url_for, Response
from flask_login import LoginManager, login_user, current_user, logout_user
from ..src.users import UsersResource
from ..src.users import User

login_manager = LoginManager()

class loginHandler:
    oauth = None

    def __init__(self, app):
        pass

    @classmethod
    def init_oauth(cls, app):
        login_manager.init_app(app)

        # oAuth Setup
        print("Registering oauth")
        cls.oauth = OAuth(app)
        cls.oauth.register(
            name='google',
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            access_token_url='https://accounts.google.com/o/oauth2/token',
            access_token_params=None,
            authorize_url='https://accounts.google.com/o/oauth2/auth',
            authorize_params=None,
            api_base_url='https://www.googleapis.com/oauth2/v1/',
            client_kwargs={'scope': 'email profile'},
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        )

    @login_manager.user_loader
    def load_user(user_id):
        return UsersResource.get_user_class_by_id(user_id)

    @classmethod
    def call_to_login(cls, app_cb):
        if cls.oauth is None:
            print("Uninitialized login handler")
            return Response("UNINITIALIZED LOGIN HANDLER", status=404, content_type="text/plain")
        redirect_uri = url_for(app_cb, _external=True)
        return cls.oauth.google.authorize_redirect(redirect_uri)

    @classmethod
    def login_cb(cls):
        if cls.oauth is None:
            print("Uninitialized login handler")
            return None
        token = cls.oauth.google.authorize_access_token()

        user_info = cls.oauth.google.get('userinfo')
        return user_info

    @classmethod
    def login_current_user(cls, user):
        UsersResource.update_db_element(user.id, "is_authenticated", "1")
        login_user(user, remember=True)

    @classmethod
    def is_verified(cls):
        return current_user.is_authenticated

    @classmethod
    def get_user_id(cls):
        return current_user.id

    @classmethod
    def load_user_data(cls):
        user_data = {
            "id": current_user.id,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "email": current_user.email
        }

        return json.dumps(user_data)

    @classmethod
    def logout(cls):
        UsersResource.update_db_element(current_user.id, "is_authenticated", "0")
        logout_user()
