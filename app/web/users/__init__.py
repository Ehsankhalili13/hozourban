from flask import Blueprint

users_bp = Blueprint("users", __name__, url_prefix="/students")

from app.web.users import routes  # noqa: E402,F401

