from flask import Blueprint, jsonify, request
import jwt as pyjwt
import jwt
import jwt as pyjwt
from config import DOMAIN, CLIENT_ID
from urllib.request import urlopen
import json
from auth0 import verify_jwt

decode_bp = Blueprint('decode', __name__, url_prefix='/decode')

@decode_bp.route('', methods=['GET'])
def decode_jwt():
    payload = verify_jwt(request)
    return payload
