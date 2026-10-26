"""Permission helpers for route protection."""
from functools import wraps

from flask import abort, flash, redirect, url_for
from flask_login import current_user


def permission_required(permission_code: str, school_id_arg: str | None = None):
    """Require a permission; optional school_id from view kwargs."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            school_id = None
            if school_id_arg and school_id_arg in kwargs:
                school_id = kwargs[school_id_arg]
            if not current_user.has_permission(permission_code, school_id=school_id):
                flash("دسترسی لازم برای این بخش را ندارید.", "error")
                abort(403)
            return fn(*args, **kwargs)

        return wrapper

    return decorator
