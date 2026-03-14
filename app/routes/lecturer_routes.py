from datetime import date

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from ..extensions import db
from ..models import Lecturer, Course, Student, Enrollment, Attendance, Result

lecturer_bp = Blueprint('lecturer', __name__, url_prefix='/lecturer')


def _get_lecturer_course(lecturer: Lecturer, course_code: str):
    """Helper: return course if it exists and belongs to this lecturer."""
    course = Course.query.filter_by(course_code=course_code).first()
    if not course:
        return None, jsonify(error="Course not found"), 404
    if course.lecturer_id != lecturer.id:
        return None, jsonify(error="You are not assigned to this course"), 403
    return course, None, None


@lecturer_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'lecturer':
        return jsonify(error="Unauthorized"), 403

    lecturer = Lecturer.query.filter_by(user_id=current_user.id).first()
    courses = Course.query.filter_by(lecturer_id=lecturer.id).all()

    total_students = 0
    for c in courses:
        total_students += Enrollment.query.filter_by(course_id=c.id).count()

    return jsonify(
        name=current_user.username,
        total_courses=len(courses),
        total_students=total_students,
        courses=[
            {"id": c.id, "course_code": c.course_code, "course_title": c.course_title}
            for c in courses
        ]
    ), 200
 
@lecturer_bp.route('/course/students', methods=['GET'])
@login_required
def get_enrolled_students():
    """
    Returns all students enrolled in a lecturer's course.
    Query param: ?course_code=CSC301
    """
    if current_user.role != 'lecturer':
        return jsonify(error="Unauthorized"), 403

    lecturer = Lecturer.query.filter_by(user_id=current_user.id).first()
    course, err_resp, err_code = _get_lecturer_course(lecturer, request.args.get('course_code'))
    if err_resp:
        return err_resp, err_code

    enrollments = Enrollment.query.filter_by(course_id=course.id).all()
    students = []
    for e in enrollments:
        student = db.session.get(Student, e.student_id)
        if student:
            students.append({
                'matric_no': student.matric_no,
                'department': student.department,
                'level': student.level,
            })

    return jsonify(students=students), 200


@lecturer_bp.route('/attendance', methods=['POST'])
@login_required
def mark_attendance():
    """
    Mark attendance for students in a course.
    Body:
    {
        "course_code": "CSC301",
        "date": "2025-03-01",          # optional — defaults to today
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
    course, err_resp, err_code = _get_lecturer_course(lecturer, data.get('course_code'))
    if err_resp:
        return err_resp, err_code

    attendance_date = (
        date.fromisoformat(data['date']) if data.get('date') else date.today()
    )

    errors, marked = [], 0

    for entry in data.get('attendance', []):
        student = Student.query.filter_by(matric_no=entry['matric_no']).first()
        if not student:
            errors.append(f"Student {entry['matric_no']} not found")
            continue

        enrolled = Enrollment.query.filter_by(
            student_id=student.id, course_id=course.id
        ).first()
        if not enrolled:
            errors.append(
                f"Student {entry['matric_no']} is not enrolled in {course.course_code}"
            )
            continue

        existing = Attendance.query.filter_by(
            student_id=student.id, course_id=course.id, date=attendance_date
        ).first()

        if existing:
            existing.status = entry['status']
        else:
            db.session.add(Attendance(
                student_id=student.id,
                course_id=course.id,
                date=attendance_date,
                status=entry['status'],
            ))

        marked += 1

    db.session.commit()

    response = {'message': f"Attendance marked for {marked} student(s)"}
    if errors:
        response['warnings'] = errors
    return jsonify(response), 200

@lecturer_bp.route('/lecturer/attendance-reports', methods=['GET'])
@login_required
def lecturer_attendance_reports():
    if current_user.role != 'lecturer':
        return jsonify(error="Unauthorized"), 403
    course_code = request.args.get('course_code')
    lecturer = Lecturer.query.filter_by(user_id=current_user.id).first()
    course = Course.query.filter_by(course_code=course_code).first()
    if not course or course.lecturer_id != lecturer.id:
        return jsonify(error="Course not found or not assigned to you"), 404
    enrollments = Enrollment.query.filter_by(course_id=course.id).all()
    report = []
    for e in enrollments:
        student = db.session.get(Student, e.student_id)
        if not student: continue
        records = Attendance.query.filter_by(
            student_id=student.id, course_id=course.id).all()
        total   = len(records)
        present = len([r for r in records if r.status == "Present"])
        rate    = round(present / total * 100, 1) if total else 0
        report.append({
            "matric_no":  student.matric_no,
            "name":       student.full_name or "—",
            "attended":   present,
            "absent":     total - present,
            "rate":       rate,
            "at_risk":    rate < 70
        })
    return jsonify(report=report, course_code=course_code), 200

@lecturer_bp.route('/results', methods=['POST'])
@login_required
def upload_results():
    """
    Upload or update scores for students in a course.
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
    course, err_resp, err_code = _get_lecturer_course(lecturer, data.get('course_code'))
    if err_resp:
        return err_resp, err_code

    errors, uploaded = [], 0

    for entry in data.get('results', []):
        student = Student.query.filter_by(matric_no=entry['matric_no']).first()
        if not student:
            errors.append(f"Student {entry['matric_no']} not found")
            continue


        enrolled = Enrollment.query.filter_by(
            student_id=student.id, course_id=course.id
        ).first()
        if not enrolled:
            errors.append(
                f"Student {entry['matric_no']} is not enrolled in {course.course_code}"
            )
            continue

        score = entry.get('score')
        if score is None or not (0 <= score <= 100):
            errors.append(f"Invalid score for {entry['matric_no']}. Must be between 0 and 100.")
            continue

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

    response = {'message': f"Results uploaded for {uploaded} student(s)"}
    if errors:
        response['warnings'] = errors
    return jsonify(response), 200
