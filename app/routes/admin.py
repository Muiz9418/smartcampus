from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from ..extensions import db
from ..models import User, Student, Lecturer, Course, Enrollment

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        return jsonify(error="Unauthorized"), 403

    return jsonify(
        total_users=User.query.count(),
        total_students=Student.query.count(),
        total_lecturers=Lecturer.query.count(),
        total_courses=Course.query.count(),
    )


@admin_bp.route('/course', methods=['POST'])
@login_required
def add_course():
    """
    Create a new course and assign it to a lecturer.
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
        lecturer_id=lecturer.id,
    )
    db.session.add(course)
    db.session.commit()
    return jsonify(message=f"Course '{course.course_title}' created and assigned successfully"), 201


@admin_bp.route('/course', methods=['GET'])
@login_required
def list_courses():
    """Returns all courses with their assigned lecturers."""
    if current_user.role != 'admin':
        return jsonify(error="Unauthorized"), 403

    courses = Course.query.all()
    result = []
    for c in courses:
        lecturer = db.session.get(Lecturer, c.lecturer_id)
        lecturer_user = db.session.get(User, lecturer.user_id) if lecturer else None
        result.append({
            'course_code': c.course_code,
            'course_title': c.course_title,
            'lecturer': lecturer_user.username if lecturer_user else 'Unassigned',
        })

    return jsonify(courses=result), 200


@admin_bp.route('/enroll', methods=['POST'])
@login_required
def enroll_student():
    """
    Manually enroll a student in a course.
    Body: { "matric_no": "U2021/001", "course_code": "CSC301" }
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

    if Enrollment.query.filter_by(student_id=student.id, course_id=course.id).first():
        return jsonify(error="Student is already enrolled in this course"), 400

    db.session.add(Enrollment(student_id=student.id, course_id=course.id))
    db.session.commit()
    return jsonify(message=f"Student {student.matric_no} enrolled in {course.course_title}"), 201


@admin_bp.route('/enroll', methods=['DELETE'])
@login_required
def unenroll_student():
    """
    Remove a student from a course.
    Body: { "matric_no": "U2021/001", "course_code": "CSC301" }
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
        student_id=student.id, course_id=course.id
    ).first()

    if not enrollment:
        return jsonify(error="Student is not enrolled in this course"), 404

    db.session.delete(enrollment)
    db.session.commit()
    return jsonify(message=f"Student {student.matric_no} removed from {course.course_title}"), 200
