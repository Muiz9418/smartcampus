from .auth import auth_bp
from .student_routes import student_bp
from .lecturer_routes import lecturer_bp
from .admin import admin_bp
from .frontend import frontend_bp

__all__ = ['auth_bp', 'student_bp', 'lecturer_bp', 'admin_bp', 'frontend_bp']
