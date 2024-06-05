from google.cloud import datastore
from config import DATASTORE_PROJECT_ID

client = datastore.Client(project=DATASTORE_PROJECT_ID)

def get_user(user_id):
    key = client.key('User', user_id)
    return client.get(key)

def get_all_users():
    query = client.query(kind='User')
    return list(query.fetch())

def get_course(course_id):
    key = client.key('Course', course_id)
    return client.get(key)

def get_all_courses(offset=0, limit=3):
    query = client.query(kind='Course')
    query.order = ['subject']
    query_iter = query.fetch(limit=limit, offset=offset)
    return list(query_iter)

def create_course(course_data):
    key = client.key('Course')
    course = datastore.Entity(key=key)
    course.update(course_data)
    client.put(course)
    return course

def update_course(course_id, course_data):
    key = client.key('Course', course_id)
    course = client.get(key)
    if course:
        course.update(course_data)
        client.put(course)
    return course

def delete_course(course_id):
    key = client.key('Course', course_id)
    client.delete(key)

def get_enrolled_students(course_id):
    query = client.query(kind='Enrollment')
    query.add_filter('course_id', '=', course_id)
    enrollments = list(query.fetch())
    student_ids = [enrollment['student_id'] for enrollment in enrollments]
    return student_ids

def enroll_student(course_id, student_id):
    key = client.key('Enrollment')
    enrollment = datastore.Entity(key=key)
    enrollment.update({
        'course_id': course_id,
        'student_id': student_id
    })
    client.put(enrollment)

def disenroll_student(course_id, student_id):
    query = client.query(kind='Enrollment')
    query.add_filter('course_id', '=', course_id)
    query.add_filter('student_id', '=', student_id)
    enrollments = list(query.fetch())
    for enrollment in enrollments:
        client.delete(enrollment.key)