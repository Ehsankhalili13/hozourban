from flask import Blueprint

school_bp = Blueprint("school", __name__, url_prefix="/schools")

from app.web.school import routes  # noqa: E402,F401
