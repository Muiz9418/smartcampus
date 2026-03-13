from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from ..extensions import db
from ..models import Student, Course, Enrollment, Attendance, Result

student_bp = Blueprint('student', __name__, url_prefix='/student')


@student_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'student':
        return jsonify(error="Unauthorized"), 403

    student = Student.query.filter_by(user_id=current_user.id).first()

    # Enrolled courses
    enrollments = Enrollment.query.filter_by(student_id=student.id).all()
    courses = []
    for e in enrollments:
        course = db.session.get(Course, e.course_id)
        if course:
            courses.append(course.course_title)

    # Attendance percentage
    attendance = Attendance.query.filter_by(student_id=student.id).all()
    present = sum(1 for a in attendance if a.status == 'Present')
    attendance_pct = round((present / len(attendance) * 100), 2) if attendance else 0

    # Results
    results = Result.query.filter_by(student_id=student.id).all()
    result_data = []
    for r in results:
        course = db.session.get(Course, r.course_id)
        result_data.append({
            'course': course.course_title if course else 'Unknown',
            'score': r.score,
            'grade': r.grade(),
        })

    return jsonify(
        courses=courses,
        attendance_percentage=attendance_pct,
        results=result_data,
    )


@student_bp.route('/courses', methods=['GET'])
@login_required
def list_courses():
    """Returns all available courses a student can browse and enroll in."""
    if current_user.role != 'student':
        return jsonify(error="Unauthorized"), 403

    courses = Course.query.all()
    return jsonify(courses=[
        {'id': c.id, 'course_code': c.course_code, 'course_title': c.course_title}
        for c in courses
    ]), 200


@student_bp.route('/enroll', methods=['POST'])
@login_required
def enroll():
    """
    Enroll the logged-in student in a course.
    Body: { "course_code": "CSC301" }
    """
    if current_user.role != 'student':
        return jsonify(error="Unauthorized"), 403

    data = request.json
    student = Student.query.filter_by(user_id=current_user.id).first()
    course = Course.query.filter_by(course_code=data.get('course_code')).first()

    if not course:
        return jsonify(error="Course not found"), 404

    already_enrolled = Enrollment.query.filter_by(
        student_id=student.id, course_id=course.id
    ).first()

    if already_enrolled:
        return jsonify(error="Already enrolled in this course"), 400

    db.session.add(Enrollment(student_id=student.id, course_id=course.id))
    db.session.commit()
    return jsonify(message=f"Successfully enrolled in {course.course_title}"), 201
