from authlib.integrations.flask_client import OAuth
from flask import current_app, jsonify, request
import requests
from config import CLIENT_ID, CLIENT_SECRET, DOMAIN


oauth = OAuth()

auth0 = oauth.register(
    'auth0',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    app_base_url=f'https://{DOMAIN}',
    access_token_url="https://" + DOMAIN + "/oauth/token",
    authorize_url="https://" + DOMAIN + "/authorize",
    client_kwargs={
        'scope': 'openid profile email'
    }
)

def auth0_login():
    content = request.get_json()
    username = content["username"]
    password = content["password"]
    body = {
        'grant_type': 'password',
        'username': username, 
        'password': password, 
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    headers = {'content-type': 'application/json'}
    url = "https://" + DOMAIN + "/oauth/token"
    r = requests.post(url, json=body, headers=headers)
    return r.text, 200, {'Content-Type': 'application/json'}