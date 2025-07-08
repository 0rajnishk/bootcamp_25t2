from datetime import timedelta
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS


app = Flask(__name__)
api = Api(app)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mad2.db'
app.config["JWT_SECRET_KEY"] = "aStrongSecretKey"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)


db = SQLAlchemy(app)
jwt = JWTManager(app)


# Define the User model for the database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='employee')
    is_approved = db.Column(db.Boolean, default=False)

    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_approved': self.is_approved
        }

# Define the Task model for the database
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'assigned_user_id': self.assigned_user_id,
            'deadline': self.deadline.strftime('%Y-%m-%d %H:%M:%S'),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


 
def create_admin():
    admin = User.query.filter_by(email="admin@mail.com").first()
    if not admin:
        admin = User(username="admin", email="admin@mail.com", password="123456", role="admin", is_approved=True)
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully.")
    else:
        print("Admin user already exists.")

with app.app_context():
    # db.drop_all()
    db.create_all()
    create_admin()



class HelloWorld(Resource):
    def get(self):
        return 'hello world from flask_rest'

class UserRegistration(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'employee')

        if not all([username, email, password]):
            return {'message': 'Missing username, email, or password'}, 400

        if User.query.filter_by(username=username).first():
            return {'message': 'Username already exists'}, 409
        if User.query.filter_by(email=email).first():
            return {'message': 'Email already exists'}, 409

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User registered successfully. Awaiting admin approval.'}, 201

class UserLogin(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            return {'message': 'Invalid credentials'}, 401

        if not user.is_approved:
            return {'message': 'Account not yet approved by admin'}, 403

        access_token = create_access_token(identity={'email': user.email, 'role': user.role, 'id': user.id}, expires_delta=timedelta(hours=24))
        return {'access_token': access_token}, 200




   

api.add_resource(HelloWorld, '/')

api.add_resource(UserRegistration, '/register')
api.add_resource(UserLogin, '/login')


if __name__ == '__main__':
    app.run()

