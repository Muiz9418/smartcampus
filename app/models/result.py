from ..extensions import db


class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)

    def grade(self) -> str:
        if self.score >= 70: return 'A'
        if self.score >= 60: return 'B'
        if self.score >= 50: return 'C'
        if self.score >= 45: return 'D'
        if self.score >= 40: return 'E'
        return 'F'
