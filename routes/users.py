from flask import Blueprint, request, jsonify
from auth0 import auth0_login, jwt_required
from models import get_user, get_all_users
from config import CLIENT_ID, CLIENT_SECRET

users_bp = Blueprint('users', __name__, url_prefix='/users')


@users_bp.route('/login', methods=['POST'])
def login():
    return auth0_login()


@users_bp.route('', methods=['GET'])
@jwt_required(role='admin')
def get_users():
    users = get_all_users()
    response = []
    for user in users:
        response.append({
            "id": user.key.id,
            "role": user['role'],
            "sub": user['sub']
        })
    return jsonify(response), 200
