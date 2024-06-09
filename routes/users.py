# import logging
import io
from flask import Blueprint, request, jsonify, send_file
from auth0 import auth0_login, jwt_required
from models import (
    get_user, get_all_users, get_user_by_sub, get_user_by_id, get_enrolled_courses_by_student, 
    check_user_avatar, save_avatar_to_storage, get_avatar_from_storage, get_all_entities, 
    delete_avatar_from_storage
)

from config import CLIENT_ID, CLIENT_SECRET, CLOUD_BUCKET
from google.cloud import storage
from google.cloud.exceptions import NotFound

# logging.basicConfig(level=logging.INFO)
users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/login', methods=['POST'])
def login():
    return auth0_login()

@users_bp.route('/', methods=['GET'])
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
    all_users = get_all_entities('User')
    return jsonify(response), 200

@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_details(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"Error": "Not found"}), 404

    current_user_role = request.current_user.get('role', '')
    if user['sub'] != request.current_user['sub'] and current_user_role != 'admin':
        return jsonify({"Error": "You don't have permission on this resource"}), 403

    response = {
        "id": user.key.id,
        "role": user['role'],
        "sub": user['sub']
    }

    avatar_url = check_user_avatar(user_id, request)
    if avatar_url:
        response["avatar_url"] = avatar_url

    if user['role'] in ['instructor', 'student']:
        courses = get_enrolled_courses_by_student(user_id)
        response['courses'] = [f"{request.url_root}courses/{course_id}" for course_id in courses]

    return jsonify(response), 200


@users_bp.route('/<int:user_id>/avatar', methods=['POST'])
@jwt_required()
def create_update_avatar(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"Error": "Not found"}), 404

    if request.current_user['sub'] != user['sub']:
        return jsonify({"Error": "You don't have permission on this resource"}), 403


    if 'file' not in request.files:
        return jsonify({"Error": "The request body is invalid"}), 400

    file = request.files['file']
    delete_avatar_from_storage(user_id)
    save_avatar_to_storage(file, user_id)
    avatar_url = f"{request.host_url}users/{user_id}/avatar"

    return jsonify({"avatar_url": avatar_url}), 200


@users_bp.route('/<int:user_id>/avatar', methods=['GET'])
@jwt_required()
def get_avatar(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"Error": "Not found"}), 404

    if request.current_user['sub'] != user['sub']:
        return jsonify({"Error": "You don't have permission on this resource"}), 403

    avatar_file = get_avatar_from_storage(user_id)

    if avatar_file:
        return send_file(avatar_file, mimetype='image/png')
    else:
        return jsonify({"Error": "Not found"}), 404

@users_bp.route('/<int:user_id>/avatar', methods=['DELETE'])
@jwt_required()
def delete_avatar(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"Error": "Not found"}), 404

    if request.current_user['sub'] != user['sub']:
        return jsonify({"Error": "You don't have permission on this resource"}), 403

    try:
        avatar_deleted = delete_avatar_from_storage(user_id)
        if not avatar_deleted:
            return jsonify({"Error": "Not found"}), 404
        return '', 204
    except Exception as e:
        # logging.error(f"Error deleting avatar: {str(e)}")
        return jsonify({"Error": "Internal Server Error"}), 500