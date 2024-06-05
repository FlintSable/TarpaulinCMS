from flask import Flask 
from routes import users, courses
from auth0 import auth0, oauth

app = Flask(__name__)
app.config.from_pyfile('config.py')

oauth.init_app(app)

app.register_blueprint(users.users_bp)
app.register_blueprint(courses.courses_bp)


if __name__ == '__main__':
    app.run(port=8080)
