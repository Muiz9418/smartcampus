import os
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import (
    LoginManager, UserMixin,
    login_user, login_required,
    logout_user, current_user
)
from datetime import date

# ----------------------
# APP CONFIG
# ----------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'smartcampus-secret-key'

# 🔧 FIX: FORCE DATABASE TO PROJECT DIRECTORY
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'smartcampus.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ----------------------
# EXTENSIONS
# ----------------------
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ----------------------
# MODELS
# ----------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student, lecturer, admin


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    matric_no = db.Column(db.String(20), unique=True)
    department = db.Column(db.String(100))
    level = db.Column(db.String(10))


class Lecturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    staff_id = db.Column(db.String(20), unique=True)
    department = db.Column(db.String(100))


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(10), unique=True)
    course_title = db.Column(db.String(100))
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturer.id'))


class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    date = db.Column(db.Date)
    status = db.Column(db.String(10))  # Present / Absent


class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    score = db.Column(db.Integer)

    def grade(self):
        if self.score >= 70: return "A"
        if self.score >= 60: return "B"
        if self.score >= 50: return "C"
        if self.score >= 45: return "D"
        if self.score >= 40: return "E"
        return "F"

# ----------------------
# LOGIN MANAGER
# ----------------------
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ----------------------
# ROUTES
# ----------------------
@app.route('/register', methods=['POST'])
def register():
    data = request.json

    if User.query.filter_by(username=data['username']).first():
        return jsonify(error="Username already exists"), 400

    hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    user = User(
        username=data['username'],
        password=hashed,
        role=data['role']
    )

    db.session.add(user)
    db.session.commit()

    if data['role'] == 'student':
        db.session.add(Student(
            user_id=user.id,
            matric_no=data['matric_no'],
            department=data['department'],
            level=data['level']
        ))

    if data['role'] == 'lecturer':
        db.session.add(Lecturer(
            user_id=user.id,
            staff_id=data['staff_id'],
            department=data['department']
        ))

    db.session.commit()
    return jsonify(message="Registered successfully"), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()

    if not user or not bcrypt.check_password_hash(user.password, data['password']):
        return jsonify(error="Invalid username or password"), 401

    login_user(user)
    return jsonify(message="Login successful", role=user.role), 200


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify(message="Logged out successfully"), 200


@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        return jsonify(error="Unauthorized"), 403

    student = Student.query.filter_by(user_id=current_user.id).first()

    enrollments = Enrollment.query.filter_by(student_id=student.id).all()
    courses = []

    for e in enrollments:
        course = db.session.get(Course, e.course_id)
        if course:
            courses.append(course.course_title)

    attendance = Attendance.query.filter_by(student_id=student.id).all()
    present = len([a for a in attendance if a.status == "Present"])
    attendance_percentage = round((present / len(attendance) * 100), 2) if attendance else 0

    results = Result.query.filter_by(student_id=student.id).all()
    result_data = []

    for r in results:
        course = db.session.get(Course, r.course_id)
        result_data.append({
            "course": course.course_title if course else "Unknown",
            "score": r.score,
            "grade": r.grade()
        })

    return jsonify(
        courses=courses,
        attendance_percentage=attendance_percentage,
        results=result_data
    )


@app.route('/lecturer/dashboard')
@login_required
def lecturer_dashboard():
    if current_user.role != 'lecturer':
        return jsonify(error="Unauthorized"), 403

    lecturer = Lecturer.query.filter_by(user_id=current_user.id).first()
    courses = Course.query.filter_by(lecturer_id=lecturer.id).all()

    return jsonify(courses=[c.course_title for c in courses])


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return jsonify(error="Unauthorized"), 403

    return jsonify(
        total_users=User.query.count(),
        total_students=Student.query.count(),
        total_lecturers=Lecturer.query.count(),
        total_courses=Course.query.count()
    )


# ----------------------
# FRONTEND ROUTING (SPA catch-all)
# ----------------------

# Serve static files from frontend
@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(basedir, 'frontend/css'), filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(basedir, 'frontend/js'), filename)

@app.route('/components/<path:filename>')
def serve_components(filename):
    return send_from_directory(os.path.join(basedir, 'frontend/components'), filename)

@app.route('/pages/<path:filename>')
def serve_pages(filename):
    return send_from_directory(os.path.join(basedir, 'frontend/pages'), filename)

# Catch-all route for SPA - serve index.html for all routes
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_spa(path):
    # Check if it's an API route (starts with /api) - don't serve SPA for API calls
    if path.startswith('api/'):
        return jsonify(error="Not found"), 404
    
    # Serve the frontend index.html for all other routes
    return send_from_directory(os.path.join(basedir, 'frontend'), 'index.html')

# ----------------------
# RUN APP
# ----------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database created at:", app.config['SQLALCHEMY_DATABASE_URI'])
    app.run(debug=True)
