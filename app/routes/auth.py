from flask import Blueprint, request, jsonify
from flask_login import login_user, login_required, logout_user

from ..extensions import db, bcrypt
from ..models import User, Student, Lecturer

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json

    if User.query.filter_by(username=data['username']).first():
        return jsonify(error="Username already exists"), 400

    hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(username=data['username'], password=hashed, role=data['role'])
    db.session.add(user)
    db.session.commit()

    if data['role'] == 'student':
        db.session.add(Student(
            user_id=user.id,
            matric_no=data['matric_no'],
            department=data['department'],
            level=data['level'],
        ))

    if data['role'] == 'lecturer':
        db.session.add(Lecturer(
            user_id=user.id,
            staff_id=data['staff_id'],
            department=data['department'],
        ))

    db.session.commit()
    return jsonify(message="Registered successfully"), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()

    if not user or not bcrypt.check_password_hash(user.password, data['password']):
        return jsonify(error="Invalid username or password"), 401

    login_user(user)
    return jsonify(message="Login successful", role=user.role), 200


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify(message="Logged out successfully"), 200
