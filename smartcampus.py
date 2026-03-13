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
# AUTH ROUTES
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


# ----------------------
# STUDENT ROUTES
# ----------------------
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


@app.route('/student/enroll', methods=['POST'])
@login_required
def student_enroll():
    """
    Allows a logged-in student to enroll in a course.
    Body: { "course_code": "CSC301" }
    """
    if current_user.role != 'student':
        return jsonify(error="Unauthorized"), 403

    data = request.json
    student = Student.query.filter_by(user_id=current_user.id).first()
    course = Course.query.filter_by(course_code=data.get('course_code')).first()

    if not course:
        return jsonify(error="Course not found"), 404

    # Prevent duplicate enrollment
    already_enrolled = Enrollment.query.filter_by(
        student_id=student.id,
        course_id=course.id
    ).first()

    if already_enrolled:
        return jsonify(error="Already enrolled in this course"), 400

    db.session.add(Enrollment(student_id=student.id, course_id=course.id))
    db.session.commit()

    return jsonify(message=f"Successfully enrolled in {course.course_title}"), 201


@app.route('/student/courses', methods=['GET'])
@login_required
def list_available_courses():
    """
    Returns all available courses a student can browse and enroll in.
    """
    if current_user.role != 'student':
        return jsonify(error="Unauthorized"), 403

    courses = Course.query.all()
    return jsonify(courses=[
        {"id": c.id, "course_code": c.course_code, "course_title": c.course_title}
        for c in courses
    ]), 200


# ----------------------
# LECTURER ROUTES
# ----------------------
@app.route('/lecturer/dashboard')
@login_required
def lecturer_dashboard():
    if current_user.role != 'lecturer':
        return jsonify(error="Unauthorized"), 403

    lecturer = Lecturer.query.filter_by(user_id=current_user.id).first()
    courses = Course.query.filter_by(lecturer_id=lecturer.id).all()

    return jsonify(courses=[
        {"id": c.id, "course_code": c.course_code, "course_title": c.course_title}
        for c in courses
    ])


@app.route('/lecturer/attendance', methods=['POST'])
@login_required
def mark_attendance():
    """
    Allows a lecturer to mark attendance for students in their course.
    Body:
    {
        "course_code": "CSC301",
        "date": "2025-03-01",           # optional, defaults to today
        "attendance": [
            {"matric_no": "U2021/001", "status": "Present"},
            {"matric_no": "U2021/002", "status": "Absent"}
        ]
    }
    """
    if current_user.role != 'lecturer':
        return jsonify(error="Unauthorized"), 403

    data = request.json
    lecturer = Lecturer.query.filter_by(user_id=current_user.id).first()
    course = Course.query.filter_by(course_code=data.get('course_code')).first()

    if not course:
        return jsonify(error="Course not found"), 404

    # Confirm the lecturer owns this course
    if course.lecturer_id != lecturer.id:
        return jsonify(error="You are not assigned to this course"), 403

    attendance_date = date.fromisoformat(data['date']) if data.get('date') else date.today()

    errors = []
    marked = 0

    for entry in data.get('attendance', []):
        student = Student.query.filter_by(matric_no=entry['matric_no']).first()

        if not student:
            errors.append(f"Student {entry['matric_no']} not found")
            continue

        # Check student is enrolled in this course
        enrolled = Enrollment.query.filter_by(
            student_id=student.id,
            course_id=course.id
        ).first()

        if not enrolled:
            errors.append(f"Student {entry['matric_no']} is not enrolled in {course.course_code}")
            continue

        # Avoid duplicate attendance entry for same date
        existing = Attendance.query.filter_by(
            student_id=student.id,
            course_id=course.id,
            date=attendance_date
        ).first()

        if existing:
            existing.status = entry['status']  # Allow update if already marked
        else:
            db.session.add(Attendance(
                student_id=student.id,
                course_id=course.id,
                date=attendance_date,
                status=entry['status']
            ))

        marked += 1

    db.session.commit()

    response = {"message": f"Attendance marked for {marked} student(s)"}
    if errors:
        response["warnings"] = errors

    return jsonify(response), 200


@app.route('/lecturer/results', methods=['POST'])
@login_required
def upload_results():
    """
    Allows a lecturer to upload or update scores for students in their course.
    Body:
    {
        "course_code": "CSC301",
        "results": [
            {"matric_no": "U2021/001", "score": 78},
            {"matric_no": "U2021/002", "score": 55}
        ]
    }
    """
    if current_user.role != 'lecturer':
        return jsonify(error="Unauthorized"), 403

    data = request.json
    lecturer = Lecturer.query.filter_by(user_id=current_user.id).first()
    course = Course.query.filter_by(course_code=data.get('course_code')).first()

    if not course:
        return jsonify(error="Course not found"), 404

    if course.lecturer_id != lecturer.id:
        return jsonify(error="You are not assigned to this course"), 403

    errors = []
    uploaded = 0

    for entry in data.get('results', []):
        student = Student.query.filter_by(matric_no=entry['matric_no']).first()

        if not student:
            errors.append(f"Student {entry['matric_no']} not found")
            continue

        enrolled = Enrollment.query.filter_by(
            student_id=student.id,
            course_id=course.id
        ).first()

        if not enrolled:
            errors.append(f"Student {entry['matric_no']} is not enrolled in {course.course_code}")
            continue

        score = entry.get('score')
        if score is None or not (0 <= score <= 100):
            errors.append(f"Invalid score for {entry['matric_no']}. Must be between 0 and 100.")
            continue

        # Update existing result or create new one
        existing = Result.query.filter_by(
            student_id=student.id,
            course_id=course.id
        ).first()

        if existing:
            existing.score = score
        else:
            db.session.add(Result(
                student_id=student.id,
                course_id=course.id,
                score=score
            ))

        uploaded += 1

    db.session.commit()

    response = {"message": f"Results uploaded for {uploaded} student(s)"}
    if errors:
        response["warnings"] = errors

    return jsonify(response), 200


@app.route('/lecturer/course/students', methods=['GET'])
@login_required
def get_enrolled_students():
    """
    Returns all students enrolled in a lecturer's course.
    Query param: ?course_code=CSC301
    """
    if current_user.role != 'lecturer':
        return jsonify(error="Unauthorized"), 403

    course_code = request.args.get('course_code')
    lecturer = Lecturer.query.filter_by(user_id=current_user.id).first()
    course = Course.query.filter_by(course_code=course_code).first()

    if not course:
        return jsonify(error="Course not found"), 404

    if course.lecturer_id != lecturer.id:
        return jsonify(error="You are not assigned to this course"), 403

    enrollments = Enrollment.query.filter_by(course_id=course.id).all()
    students = []

    for e in enrollments:
        student = db.session.get(Student, e.student_id)
        if student:
            students.append({
                "matric_no": student.matric_no,
                "department": student.department,
                "level": student.level
            })

    return jsonify(students=students), 200


# ----------------------
# ADMIN ROUTES
# ----------------------
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


@app.route('/admin/course', methods=['POST'])
@login_required
def admin_add_course():
    """
    Allows admin to create a new course and assign it to a lecturer.
    Body:
    {
        "course_code": "CSC401",
        "course_title": "Artificial Intelligence",
        "staff_id": "STAFF001"
    }
    """
    if current_user.role != 'admin':
        return jsonify(error="Unauthorized"), 403

    data = request.json

    if Course.query.filter_by(course_code=data['course_code']).first():
        return jsonify(error="Course code already exists"), 400

    lecturer = Lecturer.query.filter_by(staff_id=data.get('staff_id')).first()

    if not lecturer:
        return jsonify(error="Lecturer with that staff ID not found"), 404

    course = Course(
        course_code=data['course_code'],
        course_title=data['course_title'],
        lecturer_id=lecturer.id
    )

    db.session.add(course)
    db.session.commit()

    return jsonify(message=f"Course '{course.course_title}' created and assigned successfully"), 201


@app.route('/admin/course', methods=['GET'])
@login_required
def admin_list_courses():
    """
    Returns all courses with their assigned lecturers.
    """
    if current_user.role != 'admin':
        return jsonify(error="Unauthorized"), 403

    courses = Course.query.all()
    result = []

    for c in courses:
        lecturer = db.session.get(Lecturer, c.lecturer_id)
        lecturer_user = db.session.get(User, lecturer.user_id) if lecturer else None
        result.append({
            "course_code": c.course_code,
            "course_title": c.course_title,
            "lecturer": lecturer_user.username if lecturer_user else "Unassigned"
        })

    return jsonify(courses=result), 200


@app.route('/admin/enroll', methods=['POST'])
@login_required
def admin_enroll_student():
    """
    Allows admin to manually enroll a student in a course.
    Body:
    {
        "matric_no": "U2021/001",
        "course_code": "CSC301"
    }
    """
    if current_user.role != 'admin':
        return jsonify(error="Unauthorized"), 403

    data = request.json
    student = Student.query.filter_by(matric_no=data.get('matric_no')).first()
    course = Course.query.filter_by(course_code=data.get('course_code')).first()

    if not student:
        return jsonify(error="Student not found"), 404

    if not course:
        return jsonify(error="Course not found"), 404

    already_enrolled = Enrollment.query.filter_by(
        student_id=student.id,
        course_id=course.id
    ).first()

    if already_enrolled:
        return jsonify(error="Student is already enrolled in this course"), 400

    db.session.add(Enrollment(student_id=student.id, course_id=course.id))
    db.session.commit()

    return jsonify(message=f"Student {student.matric_no} enrolled in {course.course_title}"), 201


@app.route('/admin/enroll', methods=['DELETE'])
@login_required
def admin_unenroll_student():
    """
    Allows admin to remove a student from a course.
    Body:
    {
        "matric_no": "U2021/001",
        "course_code": "CSC301"
    }
    """
    if current_user.role != 'admin':
        return jsonify(error="Unauthorized"), 403

    data = request.json
    student = Student.query.filter_by(matric_no=data.get('matric_no')).first()
    course = Course.query.filter_by(course_code=data.get('course_code')).first()

    if not student:
        return jsonify(error="Student not found"), 404

    if not course:
        return jsonify(error="Course not found"), 404

    enrollment = Enrollment.query.filter_by(
        student_id=student.id,
        course_id=course.id
    ).first()

    if not enrollment:
        return jsonify(error="Student is not enrolled in this course"), 404

    db.session.delete(enrollment)
    db.session.commit()

    return jsonify(message=f"Student {student.matric_no} removed from {course.course_title}"), 200


# ----------------------
# FRONTEND ROUTING (SPA catch-all)
# ----------------------
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

@app.route('/')
def index():
    return send_from_directory(os.path.join(basedir, 'frontend'), 'index.html')

@app.route('/<path:path>')
def serve_spa(path):
    if path.startswith('api/'):
        return jsonify(error="Not found"), 404
    return send_from_directory(os.path.join(basedir, 'frontend'), 'index.html')


# ----------------------
# RUN APP
# ----------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database created at:", app.config['SQLALCHEMY_DATABASE_URI'])
    app.run(debug=True, port=8000)