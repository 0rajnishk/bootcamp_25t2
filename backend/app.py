from datetime import timedelta
from flask import Flask, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mad2.db'
app.config["JWT_SECRET_KEY"] = "aStrongSecretKey"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)


db = SQLAlchemy(app)
jwt = JWTManager(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {"id":self.id, "name":self.name, "email":self.email}

with app.app_context():
    # db.drop_all()
    db.create_all()


class HelloWorld(Resource):
    def get(self):
        return 'hello world from flask_rest'




class Register(Resource):
    def post(self):
        data = request.get_json()
        name = data['name']
        email = data['email']
        password = data['password']

        if not name and email:
            return "name and email are required"
        
        if User.query.filter_by(email=email).first():
            return "email already exists"
        
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return "user added successfully"

class Login(Resource):
    def post(self):
        data = request.get_json()

        user = User.query.filter_by(email=data['email'], password=data['password']).first()

        if not user:
            return "Invalid credentials"
        
        access_token = create_access_token(identity=user.email)
        return access_token

class UserResource(Resource):
    @jwt_required()
    def get(self):
        email = get_jwt_identity()
        print(email)
        users = User.query.all()
        final_users = []
        for user in users:
            final_users.append(user.to_dict())
        return final_users
    


api.add_resource(HelloWorld, '/')
api.add_resource(UserResource, '/users')
api.add_resource(Register, '/register')
api.add_resource(Login, '/login')


if __name__ == '__main__':
    app.run()

