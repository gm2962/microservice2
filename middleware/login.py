from authlib.integrations.flask_client import OAuth
import os
from flask import url_for, Response

class loginHandler:
    oauth = None

    def __init__(self, app):
        pass

    @classmethod
    def init_oauth(cls, app):
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
        return cls.oauth.google.get('userinfo')