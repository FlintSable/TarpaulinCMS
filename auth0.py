from authlib.integrations.flask_client import OAuth
from flask import current_app, jsonify, request
import requests
from functools import wraps
import jwt
from config import CLIENT_ID, CLIENT_SECRET, DOMAIN
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    if content is None or "username" not in content or "password" not in content:
        logger.warning("Invalid request payload")
        return jsonify({"Error": "The request body is invalid"}), 400
    
    username = content["username"]
    password = content["password"]
    
    logger.info(f"Login attempt for user: {username}")
    
    body = {
        'grant_type': 'password',
        'username': username,
        'password': password,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    headers = {'content-type': 'application/json'}
    url = f'https://{DOMAIN}/oauth/token'
    r = requests.post(url, json=body, headers=headers)
    
    if r.status_code == 200:
        data = r.json()
        id_token = data.get('id_token')
        if id_token:
            logger.info(f"Successful login for user: {username}")
            response = {
                'token': id_token
            }
            return jsonify(response), 200
    
    logger.warning(f"Failed login attempt for user: {username}")
    return jsonify({"Error": "Unauthorized"}), 401

def jwt_required(role=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = None
            if 'Authorization' in request.headers:
                token = request.headers['Authorization'].split(' ')[1]
            if not token:
                return jsonify({"Error": "Unauthorized"}), 401
            try:
                payload = jwt.decode(token, verify=False)
                if role and payload['role'] != role:
                    return jsonify({"Error": "You don't have permission on this resource"}), 403
            except jwt.DecodeError:
                return jsonify({"Error": "Unauthorized"}), 401
            return func(*args, **kwargs)
        return wrapper
    return decorator