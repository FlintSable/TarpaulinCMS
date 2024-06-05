from flask import Flask 
from routes import users, courses
app = Flask(__name__)

app.register_blueprint(users.blueprint)
app.register_blueprint(courses.blueprint)


if __name__ == '__main__':
    app.run()
