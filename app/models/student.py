from ..extensions import db


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    matric_no = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(100))
    level = db.Column(db.String(10))
