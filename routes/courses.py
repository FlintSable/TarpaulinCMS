from flask import Blueprint, request, jsonify
from auth0 import jwt_required
from models import get_course, get_all_courses, create_course, update_course, delete_course, get_enrolled_students, enroll_student, disenroll_student

courses_bp = Blueprint('courses', __name__, url_prefix='/courses')

@courses_bp.route('', methods=['POST'])
@jwt_required(role='admin')
def create_new_course():
    course_data = request.get_json()
    course = create_course(course_data)
    return jsonify(course), 201

@courses_bp.route('', methods=['GET'])
def get_courses():
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 3, type=int)
    courses = get_all_courses(offset, limit)
    
    response = {
        "courses": courses
    }
    if len(courses) == limit:
        response["next"] = f"/courses?offset={offset + limit}&limit={limit}"
    
    return jsonify(response), 200

@courses_bp.route('/<int:course_id>', methods=['GET'])
def get_course_details(course_id):
    course = get_course(course_id)
    if not course:
        return jsonify({"Error": "Not found"}), 404
    return jsonify(course), 200

@courses_bp.route('/<int:course_id>', methods=['PATCH'])
@jwt_required(role='admin')
def update_course_details(course_id):
    course_data = request.get_json()
    course = update_course(course_id, course_data)
    if not course:
        return jsonify({"Error": "Not found"}), 404
    return jsonify(course), 200

@courses_bp.route('/<int:course_id>', methods=['DELETE'])
@jwt_required(role='admin')
def delete_course_route(course_id):
    delete_course(course_id)
    return '', 204

@courses_bp.route('/<int:course_id>/students', methods=['GET'])
@jwt_required()
def get_course_enrollment(course_id):
    students = get_enrolled_students(course_id)
    return jsonify(students), 200

@courses_bp.route('/<int:course_id>/students', methods=['PATCH'])
@jwt_required()
def update_course_enrollment(course_id):
    enrollment_data = request.get_json()
    
    for student_id in enrollment_data['add']:
        enroll_student(course_id, student_id)
    
    for student_id in enrollment_data['remove']:
        disenroll_student(course_id, student_id)
    
    return '', 204