from flask import Blueprint, request, jsonify
from auth0 import jwt_required
from models import get_course, get_all_courses, create_course, get_user_by_id, update_course, delete_course, get_enrolled_students, enroll_student, disenroll_student

courses_bp = Blueprint('courses', __name__, url_prefix='/courses')

@courses_bp.route('', methods=['POST'])
@jwt_required(role='admin')
def create_new_course():
    content = request.get_json()
    required_fields = ['subject', 'number', 'title', 'term', 'instructor_id']
    if not content or not all(field in content for field in required_fields):
        return jsonify({"Error": "The request body is invalid"}), 400
    
    instructor_id = content['instructor_id']
    if not get_user_by_id(instructor_id) or get_user_by_id(instructor_id)['role'] != 'instructor':
        return jsonify({"Error": "The request body is invalid"}), 400
    
    try:
        base_url = request.base_url
        course = create_course(content, base_url)
        return jsonify(course), 201
    except ValueError as e:
        return jsonify({"Error": str(e)}), 400

@courses_bp.route('', methods=['GET'])
def get_courses():
    offset = request.args.get('offset', default=0, type=int)
    limit = request.args.get('limit', default=3, type=int)
    base_url = request.base_url

    courses = get_all_courses(offset, limit, base_url)
    # return jsonify(courses), 200
    return jsonify(courses), 200

@courses_bp.route('/<int:course_id>', methods=['GET'])
def get_course_details(course_id):
    base_url = request.base_url
    course = get_course(course_id)
    if not course:
        return jsonify({"Error": "Not found"}), 404

    return jsonify({
        "id": course.key.id,
        "subject": course['subject'],
        "number": course['number'],
        "title": course['title'],
        "term": course['term'],
        "instructor_id": course['instructor_id'],
        "self": base_url
    }), 200

@courses_bp.route('/<int:course_id>', methods=['PATCH'])
@jwt_required(role='admin')
def update_course_details(course_id):
    content = request.get_json()
    if not content:
        return jsonify({"Error": "The request body is invalid"}), 400

    try:
        course = update_course(course_id, content)
        if not course:
            return jsonify({"Error": "Not found"}), 404
        return jsonify(course), 200
    except ValueError as e:
        return jsonify({"Error": str(e)}), 400

@courses_bp.route('/<int:course_id>', methods=['DELETE'])
@jwt_required(role='admin')
def delete_course_route(course_id):
    try:
        delete_course(course_id)
        return '', 204
    except ValueError:
        return jsonify({"Error": "No course with this course_id exists"}), 403

@courses_bp.route('/<int:course_id>', methods=['PATCH'])
@jwt_required()
def update_course(course_id):
    content = request.get_json()

    user_id = request.current_user['sub']
    if request.current_user['role'] != 'admin':
        return jsonify({"Error": "You don't have permission on this resource"}), 403

    course, error = update_course(course_id, content)
    if not course:
        if error:
            return jsonify({"Error": error}), 400
        else:
            return jsonify({"Error": "Not found"}), 404

    return jsonify(course), 200

@courses_bp.route('/<int:course_id>/students', methods=['GET'])
@jwt_required()
def get_enrolled_students_route(course_id):
    course = get_course(course_id)
    if not course:
        return jsonify({"Error": "Not found"}), 404

    user_id = request.current_user['sub']
    if request.current_user['role'] != 'admin' and course['instructor_id'] != user_id:
        return jsonify({"Error": "You don't have permission on this resource"}), 403

    students = get_enrolled_students(course_id)
    return jsonify(students), 200

@courses_bp.route('/<int:course_id>/students', methods=['PATCH'])
@jwt_required()
def update_enrollment(course_id):
    content = request.get_json()
    if not content or 'add' not in content or 'remove' not in content:
        return jsonify({"Error": "The request body is invalid"}), 400

    course = get_course(course_id)
    if not course:
        return jsonify({"Error": "Not found"}), 404

    user_id = request.current_user['sub']
    if request.current_user['role'] != 'admin' and course['instructor_id'] != user_id:
        return jsonify({"Error": "You don't have permission on this resource"}), 403

    student_ids_to_add = content['add']
    student_ids_to_remove = content['remove']

    try:
        enroll_student(course_id, student_ids_to_add, student_ids_to_remove)
        return '', 200
    except ValueError as e:
        return jsonify({"Error": str(e)}), 409