from flask import Blueprint, request, jsonify
from auth import jwt_required
from models import get_user, get_all_users

blueprint = Blueprint('users', __name__, url_prefix='/users')

@blueprint.route('', methods=['GET'])
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
