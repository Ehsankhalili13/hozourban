from flask import Blueprint

setup_bp = Blueprint("setup", __name__, url_prefix="/setup")

from app.web.setup import routes  # noqa: E402,F401
