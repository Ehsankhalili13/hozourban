from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import User
from app.web.setup import setup_bp


def needs_setup() -> bool:
    """Return True when no user exists yet (first-run state)."""
    try:
        return db.session.execute(db.select(User.id).limit(1)).scalar_one_or_none() is None
    except Exception:
        # Tables may not exist yet.
        return True


def ensure_tables() -> None:
    """Create tables if they do not exist yet (bootstrap convenience)."""
    db.create_all()


@setup_bp.route("/", methods=["GET", "POST"])
def index():
    ensure_tables()

    if not needs_setup():
        # Setup already done — send user to login or dashboard.
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        full_name = request.form.get("full_name", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        errors = []
        if not username:
            errors.append("نام کاربری الزامی است.")
        if not full_name:
            errors.append("نام کامل الزامی است.")
        if len(password) < 12:
            errors.append("رمز عبور باید حداقل ۱۲ نویسه باشد.")
        if password != confirm:
            errors.append("رمز عبور و تکرار آن یکسان نیستند.")

        if errors:
            for msg in errors:
                flash(msg, "error")
            return render_template(
                "setup/index.html",
                username=username,
                full_name=full_name,
            )

        user = User(
            username=username,
            full_name=full_name,
            is_active=True,
            is_system_admin=True,
        )
        user.set_password(password)
        db.session.add(user)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("این نام کاربری قبلاً ثبت شده است.", "error")
            return render_template(
                "setup/index.html",
                username=username,
                full_name=full_name,
            )

        login_user(user)
        flash("حساب مدیر اصلی با موفقیت ساخته شد. به حضوربان خوش آمدید.", "success")
        return redirect(url_for("dashboard"))

    return render_template("setup/index.html")
