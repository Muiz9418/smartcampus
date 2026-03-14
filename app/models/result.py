from ..extensions import db


class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    ca_score = db.Column(db.Integer, default=0, nullable=False)
    exam_score = db.Column(db.Integer, default=0, nullable=False)
    submitted = db.Column(db.Boolean, default=False)
    approved = db.Column(db.Boolean, default=False)

    @property
    def total(self):
        return self.ca_score + self.exam_score

    def grade(self) -> str:
        s = self.total
        if s >= 70:
            return 'A'
        if s >= 60:
            return 'B'
        if s >= 50:
            return 'C'
        if s >= 45:
            return 'D'
        if s >= 40:
            return 'E'
        return 'F'
