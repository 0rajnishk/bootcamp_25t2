from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"


class HelloWorld(Resource):
    def get(self):
        return 'hello world from flask_rest'

api.add_resource(HelloWorld, '/')


if __name__ == '__main__':
    app.run()

