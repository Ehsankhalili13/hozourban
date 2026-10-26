from flask import Blueprint

attendance_bp = Blueprint("attendance", __name__, url_prefix="/attendance")

from app.web.attendance import routes  # noqa: E402,F401

