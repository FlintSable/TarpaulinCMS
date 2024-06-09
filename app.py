from flask import Flask, jsonify 
from routes import users, courses
from auth0 import auth0, oauth
import os

app = Flask(__name__)
app.config.from_pyfile('config.py')

# print("Environment Variables:")
# print(f"CLIENT_ID: {os.environ.get('CLIENT_ID')}")
# print(f"CLIENT_SECRET: {os.environ.get('CLIENT_SECRET')}")
# print(f"DOMAIN: {os.environ.get('DOMAIN')}")
# print(f"DATASTORE_PROJECT_ID: {os.environ.get('DATASTORE_PROJECT_ID')}")
# print(f"CLOUD_BUCKET: {os.environ.get('CLOUD_BUCKET')}")
# print(f"FLASK_ENV: {os.environ.get('FLASK_ENV')}")

oauth.init_app(app)

app.register_blueprint(users.users_bp)
app.register_blueprint(courses.courses_bp)
# app.register_blueprint(decode.decode_bp)
@app.route('/')
def home():
    return jsonify({
        'message': 'Welcome to the Tarpaulin CMS API!',
        'endpoints': [
            {
                'name': 'User Login',
                'method': 'POST',
                'path': '/users/login',
                'description': 'Generate a JWT for a registered user by sending a request to Auth0.'
            },
            {
                'name': 'Get All Users',
                'method': 'GET',
                'path': '/users',
                'description': 'Return an array with all 9 pre-created users. Admin only.'
            },
            {
                'name': 'Get User Details',
                'method': 'GET',
                'path': '/users/:user_id',
                'description': 'Return the details of a user. Admin or user with JWT matching user_id.'
            },
            {
                'name': 'Create/Update User Avatar',
                'method': 'POST',
                'path': '/users/:user_id/avatar',
                'description': 'Upload a .png file as the user\'s avatar.'
            },
            {
                'name': 'Get User Avatar',
                'method': 'GET',
                'path': '/users/:user_id/avatar',
                'description': 'Return the user\'s avatar file.'
            },
            {
                'name': 'Delete User Avatar',
                'method': 'DELETE',
                'path': '/users/:user_id/avatar',
                'description': 'Delete the user\'s avatar file.'
            },
            {
                'name': 'Create Course',
                'method': 'POST',
                'path': '/courses',
                'description': 'Create a new course. Admin only.'
            },
            {
                'name': 'Get All Courses',
                'method': 'GET',
                'path': '/courses',
                'description': 'Return a paginated list of courses. Unprotected.'
            },
            {
                'name': 'Get Course Details',
                'method': 'GET',
                'path': '/courses/:course_id',
                'description': 'Return the details of a course. Unprotected.'
            },
            {
                'name': 'Update Course',
                'method': 'PATCH',
                'path': '/courses/:course_id',
                'description': 'Perform a partial update on a course. Admin only.'
            },
            {
                'name': 'Delete Course',
                'method': 'DELETE',
                'path': '/courses/:course_id',
                'description': 'Delete a course and its enrollment data. Admin only.'
            },
            {
                'name': 'Update Course Enrollment',
                'method': 'PATCH',
                'path': '/courses/:course_id/students',
                'description': 'Enroll and/or disenroll students from a course. Admin or instructor of the course.'
            },
            {
                'name': 'Get Course Enrollment',
                'method': 'GET',
                'path': '/courses/:course_id/students',
                'description': 'Get the list of students enrolled in a course. Admin or instructor of the course.'
            }
        ],
        'documentation': 'Refer to the API specification document for detailed information on request/response formats and status codes.'
    })


if __name__ == '__main__':
    app.run(port=8080, debug=True)
