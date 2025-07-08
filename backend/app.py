from datetime import timedelta
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from functools import wraps


app = Flask(__name__)
api = Api(app)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mad2.db'
app.config["JWT_SECRET_KEY"] = "aStrongSecretKey"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)


db = SQLAlchemy(app)
jwt = JWTManager(app)

def role_required(allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            current_user_identity = get_jwt_identity()
            current_user_role = current_user_identity['role']
            if current_user_role not in allowed_roles:
                return {'message': 'Access forbidden: Insufficient role privileges'}, 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

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
        admin = User(username="admin", email="admin@mail.com", password=generate_password_hash("123456"), role="admin", is_approved=True)
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

class SignupResource(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not all([username, email, password]):
            return {'message': 'Missing username, email, or password'}, 400

        if User.query.filter_by(username=username).first():
            return {'message': 'Username already exists'}, 409
        if User.query.filter_by(email=email).first():
            return {'message': 'Email already exists'}, 409

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password, role='employee', is_approved=False)
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User registered successfully. Awaiting admin approval.'}, 201

class LoginResource(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        print(email, password)
        user = User.query.filter_by(email=email).first()
        print(user)
        if not user or not check_password_hash(user.password, password):
            return {'message': 'Invalid credentials'}, 401

        if not user.is_approved:
            return {'message': 'Account not yet approved by admin'}, 403

        access_token = create_access_token(identity={'email': user.email, 'role': user.role, 'id': user.id}, expires_delta=timedelta(hours=24))
        return {'access_token': access_token}, 200

class UsersResource(Resource):
    @role_required(['admin'])
    def get(self, user_id=None):
        if user_id:
            user = User.query.get(user_id)
            if not user:
                return {'message': 'User not found'}, 404
            return user.to_json(), 200
        else:
            users = User.query.all()
            return [user.to_json() for user in users], 200

    @role_required(['admin'])
    def put(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404

        data = request.get_json()
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.role = data.get('role', user.role)
        user.is_approved = data.get('is_approved', user.is_approved)

        db.session.commit()
        return {'message': 'User updated successfully'}, 200

    @role_required(['admin'])
    def delete(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404

        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted successfully'}, 200

class TaskResource(Resource):
    @role_required(['admin', 'manager'])
    def post(self):
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        status = data.get('status', 'open')
        deadline_str = data.get('deadline')
        assigned_user_id = data.get('assigned_user_id')

        if not all([title, description, deadline_str, assigned_user_id]):
            return {'message': 'Missing title, description, deadline, or assigned_user_id'}, 400

        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return {'message': 'Invalid deadline format. Use YYYY-MM-DD HH:MM:SS'}, 400

        assigned_user = User.query.get(assigned_user_id)
        if not assigned_user:
            return {'message': 'Assigned user not found'}, 404

        new_task = Task(title=title, description=description, status=status, deadline=deadline, created_at=datetime.utcnow(), assigned_user_id=assigned_user_id)
        db.session.add(new_task)
        db.session.commit()
        return {'message': 'Task created successfully', 'task': new_task.to_json()}, 201

    @jwt_required()
    def get(self, task_id=None):
        current_user_identity = get_jwt_identity()
        current_user_role = current_user_identity['role']
        current_user_id = current_user_identity['id']

        if task_id:
            task = Task.query.get(task_id)
            if not task:
                return {'message': 'Task not found'}, 404
            
            if current_user_role == 'employee' and task.assigned_user_id != current_user_id:
                return {'message': 'Unauthorized to view this task'}, 403
            
            return task.to_json(), 200
        else:
            if current_user_role == 'employee':
                tasks = Task.query.filter_by(assigned_user_id=current_user_id).all()
            else:
                tasks = Task.query.all()
            return [task.to_json() for task in tasks], 200

    @jwt_required()
    def put(self, task_id):
        current_user_identity = get_jwt_identity()
        current_user_role = current_user_identity['role']
        current_user_id = current_user_identity['id']

        task = Task.query.get(task_id)
        if not task:
            return {'message': 'Task not found'}, 404

        if current_user_role == 'employee' and task.assigned_user_id != current_user_id:
            return {'message': 'Unauthorized to modify this task'}, 403

        data = request.get_json()
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.status = data.get('status', task.status)
        
        if 'deadline' in data:
            try:
                task.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return {'message': 'Invalid deadline format. Use YYYY-MM-DD HH:MM:%S'}, 400

        if 'assigned_user_id' in data:
            if current_user_role not in ['admin', 'manager']:
                return {'message': 'Unauthorized to reassign tasks'}, 403
            assigned_user = User.query.get(data['assigned_user_id'])
            if not assigned_user:
                return {'message': 'Assigned user not found'}, 404
            task.assigned_user_id = data['assigned_user_id']

        db.session.commit()
        return {'message': 'Task updated successfully', 'task': task.to_json()}, 200

    @role_required(['admin', 'manager'])
    def delete(self, task_id):
        task = Task.query.get(task_id)
        if not task:
            return {'message': 'Task not found'}, 404

        db.session.delete(task)
        db.session.commit()
        return {'message': 'Task deleted successfully'}, 200

class AllUsersResource(Resource):
    @role_required(['admin', 'manager'])
    def get(self):
        users = User.query.all()
        return [user.to_json() for user in users], 200




   

api.add_resource(HelloWorld, '/') # Home endpoint
api.add_resource(SignupResource, '/signup') # User signup endpoint
api.add_resource(LoginResource, '/login') # User login endpoint
api.add_resource(UsersResource,'/admin/users', '/admin/users/<int:user_id>') # Admin user management endpoint
api.add_resource(TaskResource, '/task', '/task/<int:task_id>') # Task management endpoint
api.add_resource(AllUsersResource, '/all_users') # Endpoint to get all users (for admin and manager)


if __name__ == '__main__':
    app.run()

