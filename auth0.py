from authlib.integrations.flask_client import OAuth
from flask import current_app, jsonify, request
import requests
from functools import wraps
from jwt.exceptions import DecodeError
import jwt
from six.moves.urllib.request import urlopen
from jose import jwt, JWTError
from urllib.request import urlopen

from config import CLIENT_ID, CLIENT_SECRET, DOMAIN
from models import get_user, get_user_by_sub
import json
import logging
from six.moves.urllib.request import urlopen

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

oauth = OAuth()
ALGORITHMS = ["RS256"]

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

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


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
        jwt_token = data.get('id_token')
        if jwt_token:
            logger.info(f"Successful login for user: {username}")
            response = {
                'token': jwt_token
            }
            return jsonify(response), 200

    logger.warning(f"Failed login attempt for user: {username}")
    return jsonify({"Error": "Unauthorized"}), 401

def extract_token_from_header():
    auth_header = request.headers.get("Authorization", None)
    if not auth_header:
        return None

    auth_header_parts = auth_header.split()
    if len(auth_header_parts) != 2 or auth_header_parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header", "description": "Invalid Authorization header format"}, 401)

    return auth_header_parts[1]

# def jwt_required(role=None):
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             token = extract_token_from_header()
#             if not token:
#                 raise AuthError({"code": "no auth header", "description": "Authorization header is missing"}, 401)

#             payload = verify_jwt(token)
#             if not payload:
#                 raise AuthError({"code": "invalid_token", "description": "Invalid token"}, 401)

#             if role:
#                 user = get_user(payload['sub'])
#                 if not user or user['role'] != role:
#                     raise AuthError({"code": "insufficient_permissions", "description": "Insufficient permissions"}, 403)

#             request.current_user = payload
#             return func(*args, **kwargs)

#         return wrapper

#     return decorator

# def jwt_required(role=None):
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             token = extract_token_from_header()
#             if not token:
#                 raise AuthError({"code": "no auth header", "description": "Authorization header is missing"}, 401)

#             payload = verify_jwt(token)
#             if not payload:
#                 raise AuthError({"code": "invalid_token", "description": "Invalid token"}, 401)

#             if role:
#                 user_id = payload['sub']
#                 logging.info(f"User ID (sub) from JWT: {user_id}")
#                 user = get_user_by_sub(user_id)
#                 logging.info(f"User object from Datastore: {user}")
#                 if not user:
#                     raise AuthError({"code": "user_not_found", "description": "User not found"}, 404)
#                 logger.info(f"User role: {user['role']}, Required role: {role}")
#                 if user['role'] != role:
#                     raise AuthError({"code": "insufficient_permissions", "description": "Insufficient permissions"}, 403)

#             request.current_user = payload
#             return func(*args, **kwargs)

#         return wrapper

#     return decorator

def jwt_required(role=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = extract_token_from_header()
            if not token:
                return jsonify({"Error": "Unauthorized"}), 401

            try:
                payload = verify_jwt(token)
            except AuthError as e:
                return jsonify({"Error": "Unauthorized"}), 401

            if role:
                user_id = payload['sub']
                user = get_user_by_sub(user_id)
                if not user or user['role'] != role:
                    return jsonify({"Error": "You don't have permission on this resource"}), 403

            request.current_user = payload
            return func(*args, **kwargs)

        return wrapper

    return decorator

def verify_jwt(token):
    jsonurl = urlopen(f"https://{DOMAIN}/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.JWTError:
        raise AuthError({"code": "invalid_header", "description": "Invalid header. Use an RS256 signed JWT Access Token"}, 401)
    if unverified_header["alg"] == "HS256":
        raise AuthError({"code": "invalid_header", "description": "Invalid header. Use an RS256 signed JWT Access Token"}, 401)
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=CLIENT_ID,
                issuer=f"https://{DOMAIN}/"
            )
            logging.info(f"Decoded JWT payload: {payload}")
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthError({"code": "token_expired", "description": "token is expired"}, 401)
        except jwt.JWTClaimsError:
            raise AuthError({"code": "invalid_claims", "description": "incorrect claims, please check the audience and issuer"}, 401)
        except Exception:
            raise AuthError({"code": "invalid_header", "description": "Unable to parse authentication token."}, 401)

        return payload
    else:
        raise AuthError({"code": "no_rsa_key", "description": "No RSA key in JWKS"}, 401)
