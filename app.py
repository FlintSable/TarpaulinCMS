from flask import Flask 
from routes import users, courses, decode
from auth0 import auth0, oauth
import logging

app = Flask(__name__)
app.config.from_pyfile('config.py')


oauth.init_app(app)

app.register_blueprint(users.users_bp)
app.register_blueprint(courses.courses_bp)
app.register_blueprint(decode.decode_bp)

if __name__ == '__main__':
    app.run(port=8080, debug=True)
