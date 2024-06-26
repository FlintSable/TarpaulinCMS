from google.cloud.exceptions import NotFound
from io import BytesIO
from google.cloud import storage
from config import CLOUD_BUCKET
from google.cloud import datastore
from config import DATASTORE_PROJECT_ID
client = datastore.Client(project=DATASTORE_PROJECT_ID)


def get_user(sub):
    query = client.query(kind='users')
    query.add_filter('sub', '=', sub)
    results = list(query.fetch(limit=1))
    if results:
        return results[0]
    return None

def get_all_users():
    query = client.query(kind='users')
    return list(query.fetch())

def get_user_by_sub(sub):
    query = client.query(kind='users')
    query.add_filter('sub', '=', sub)
    users = list(query.fetch())
    if users:
        return users[0]
    else:
        return None

def get_user_role(user_id):
    key = client.key('users', user_id)
    user = client.get(key)
    if user:
        return user.get('role')
    return None

def get_all_entities(kind):
    query = client.query(kind=kind)
    entities = list(query.fetch())
    return entities

def get_user_by_id(user_id):
    key = client.key('users', user_id)
    user = client.get(key)
    return user

def save_avatar_to_storage(file, user_id):
    blob_name = f'avatars/{user_id}.png'

    storage_client = storage.Client()
    bucket = storage_client.bucket(CLOUD_BUCKET)
    blob = bucket.blob(blob_name)

    blob.upload_from_file(file)

    avatar_url = f'https://storage.googleapis.com/{CLOUD_BUCKET}/{blob_name}'
    return avatar_url

def check_user_avatar(user_id, request):
    # logging.info(f"Checking avatar for user: {user_id}")
    blob_name = f'avatars/{user_id}.png'
    storage_client = storage.Client()
    bucket = storage_client.bucket(CLOUD_BUCKET)

    try:
        blob = bucket.blob(blob_name)
        if blob.exists():
            avatar_url = f"{request.host_url}users/{user_id}/avatar"
            return avatar_url
        else:
            return None
    except Exception as e:
        return None

def get_avatar_from_storage(user_id):
    blob_name = f'avatars/{user_id}.png'
    storage_client = storage.Client()
    bucket = storage_client.bucket(CLOUD_BUCKET)

    try:
        blob = bucket.blob(blob_name)
        if blob.exists():
            avatar_data = blob.download_as_bytes()
            avatar_file = BytesIO(avatar_data)
            return avatar_file
        else:
            return None
    except Exception as e:
        return None

def delete_avatar_from_storage(user_id):
    blob_name = f'avatars/{user_id}.png'
    storage_client = storage.Client()
    bucket = storage_client.bucket(CLOUD_BUCKET)

    try:
        blob = bucket.blob(blob_name)
        if blob.exists():
            blob.delete()
            return True
        else:
            # logging.info(f"No avatar file found to delete for user: {user_id}")
            return False
    except Exception as e:
        raise

def get_course(course_id):
    key = client.key('Course', course_id)
    course = client.get(key)
    return course

def get_all_courses(offset=0, limit=3, base_url=""):
    query = client.query(kind='Course')
    query.order = ['subject']
    results = list(query.fetch(limit=limit, offset=offset))
    courses = []
    for result in results:
        course = {
            "id": result.key.id,
            "subject": result['subject'],
            "number": result['number'],
            "title": result['title'],
            "instructor_id": result['instructor_id'],
            "term": result.get('term', ''),
            "self": f"{base_url}/{result.key.id}"
        }
        courses.append(course)

    next_offset = offset + limit
    next_url = f"{base_url}?offset={next_offset}&limit={limit}" if len(results) == limit else None

    response = {
        "courses": courses,
        "next": next_url
    }
    return response

def create_course(data, base_url):
    course_key = client.key('Course')
    course = datastore.Entity(key=course_key)
    course.update(data)
    client.put(course)
    course["id"] = course.key.id
    course["self"] = f"{base_url}/{course.key.id}"
    return course

def update_course(course_id, data):
    key = client.key('Course', course_id)
    course = client.get(key)
    if course:
        if 'subject' in data:
            course['subject'] = data['subject']
        if 'number' in data:
            course['number'] = data['number']
        if 'title' in data:
            course['title'] = data['title']
        if 'term' in data:
            course['term'] = data['term']
        if 'instructor_id' in data:
            instructor_role = get_user_role(data['instructor_id'])
            if instructor_role != 'instructor':
                return None, "The request body is invalid"
            course['instructor_id'] = data['instructor_id']
        client.put(course)
        updated_course = {
            "id": course.key.id,
            "subject": course['subject'],
            "number": course['number'],
            "title": course['title'],
            "instructor_id": course['instructor_id'],
            "term": course['term']
        }
        return updated_course, None
    return None, "Course not found"


def delete_course(course_id):
    key = client.key('Course', course_id)
    course = client.get(key)
    if course:
        query = client.query(kind='enrollment')
        query.add_filter('course_id', '=', course_id)
        enrollments = list(query.fetch())
        for enrollment in enrollments:
            client.delete(enrollment.key)
        
        client.delete(key)
    else:
        raise ValueError("No course with this course_id exists")

def enroll_student(course_id, student_ids_to_add, student_ids_to_remove):
    course_key = client.key('Course', course_id)
    course = client.get(course_key)
    if not course:
        raise ValueError("Course not found")
    
    for student_id in student_ids_to_add:
        student_key = client.key('users', student_id)
        student = client.get(student_key)
        if not student or student['role'] != 'student':
            raise ValueError("Invalid student ID")
        
        enrollment_key = client.key('enrollment', f"{course_id}_{student_id}")
        enrollment = client.get(enrollment_key)
        if not enrollment:
            enrollment = datastore.Entity(key=enrollment_key)
            enrollment['course_id'] = course_id
            enrollment['student_id'] = student_id
            client.put(enrollment)
    
    for student_id in student_ids_to_remove:
        enrollment_key = client.key('enrollment', f"{course_id}_{student_id}")
        enrollment = client.get(enrollment_key)
        if enrollment:
            # Delete the enrollment
            client.delete(enrollment_key)

def get_enrolled_students(course_id):
    query = client.query(kind='enrollment')
    query.add_filter('course_id', '=', course_id)
    enrollments = list(query.fetch())
    student_ids = [enrollment['student_id'] for enrollment in enrollments]
    return student_ids

def disenroll_student(course_id, student_id):
    query = client.query(kind='enrollment')
    query.add_filter('course_id', '=', course_id)
    query.add_filter('student_id', '=', student_id)
    enrollments = list(query.fetch())
    for enrollment in enrollments:
        client.delete(enrollment.key)

def get_enrolled_courses_by_student(student_id):
    query = client.query(kind='enrollment')
    query.add_filter('student_id', '=', student_id)
    enrollments = list(query.fetch())
    course_ids = [enrollment['course_id'] for enrollment in enrollments]    
    return course_ids