from flask import Blueprint

academics_bp = Blueprint("academics", __name__, url_prefix="/classes")

from app.web.academics import routes  # noqa: E402,F401
