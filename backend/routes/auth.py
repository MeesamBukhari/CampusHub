from flask import Blueprint, request, jsonify, session
from extensions import db, bcrypt
from models import User
from utils import log_audit

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'student') # Default to student

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, email=email, password_hash=hashed_pw, role=role)
    
    db.session.add(new_user)
    db.session.commit()
    
    log_audit('CREATE', 'users', new_user.id, f"Registered new user: {username}")
    
    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password_hash, password):
        session.permanent = True
        session['user_id'] = user.id
        session['role'] = user.role
        
        log_audit('LOGIN', 'users', user.id, "User logged in")
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200

    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    uid = session.get('user_id')
    if uid:
        log_audit('LOGOUT', 'users', uid, "User logged out")
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/me', methods=['GET'])
def check_session():
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {'id': session['user_id'], 'role': session['role']}
        }), 200
    return jsonify({'authenticated': False}), 401