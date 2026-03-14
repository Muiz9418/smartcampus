from flask import Blueprint, app, request, jsonify
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

    # Gpa calculation 
    if results:
        grade_points = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1, "F": 0}
        gpa = round(sum(grade_points.get(r.grade(), 0) for r in results) / len(results), 2)



    return jsonify(
        courses=courses,
        attendance_percentage=attendance_pct,
        results=result_data,
        gpa=gpa,
        name= current_user.username
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
    
@student_bp.route('/student/attendance-detail', methods=['GET'])
@login_required
def student_attendance_detail():
    if current_user.role != 'student':
        return jsonify(error="Unauthorized"), 403
    student = Student.query.filter_by(user_id=current_user.id).first()
    enrollments = Enrollment.query.filter_by(student_id=student.id).all()
    breakdown = []
    for e in enrollments:
        course = db.session.get(Course, e.course_id)
        if not course: continue
        records = Attendance.query.filter_by(
            student_id=student.id, course_id=course.id).all()
        total = len(records)
        present = len([r for r in records if r.status == "Present"])
        rate = round(present / total * 100, 1) if total else 0
        breakdown.append({
            "course_code":  course.course_code,
            "course_title": course.course_title,
            "attended": present, "total": total,
            "absent": total - present,
            "rate": rate,
            "at_risk": rate < 70
        })
    return jsonify(breakdown=breakdown), 200

@student_bp.route('/student/grades-detail', methods=['GET'])
@login_required
def student_grades_detail():
    if current_user.role != 'student':
        return jsonify(error="Unauthorized"), 403
    student = Student.query.filter_by(user_id=current_user.id).first()
    results = Result.query.filter_by(student_id=student.id).all()
    data = []
    total_gp = 0
    total_units = 0
    for r in results:
        course = db.session.get(Course, r.course_id)
        if not course: continue
        units = 3  # default; extend model to store units if needed
        gp = {"A":5,"B":4,"C":3,"D":2,"E":1}.get(r.grade(), 0) * units
        total_gp += gp
        total_units += units
        data.append({
            "course_code":  course.course_code,
            "course_title": course.course_title,
            "ca_score":   r.ca_score,
            "exam_score": r.exam_score,
            "total":      r.total,
            "grade":      r.grade(),
            "grade_points": gp
        })
    gpa = round(total_gp / total_units, 2) if total_units else 0
    return jsonify(results=data, gpa=gpa, total_units=total_units), 200


    db.session.add(Enrollment(student_id=student.id, course_id=course.id))
    db.session.commit()
    return jsonify(message=f"Successfully enrolled in {course.course_title}"), 201
