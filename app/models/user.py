from flask_login import UserMixin
from ..extensions import db, login_manager


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student | lecturer | admin


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
