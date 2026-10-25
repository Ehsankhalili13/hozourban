from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user, login_required

from app.extensions import db
from app.models import User
from app.web.auth import auth_bp


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = db.session.execute(
            db.select(User).where(User.username == username)
        ).scalar_one_or_none()

        if user and user.is_active and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))

        flash("نام کاربری یا رمز عبور نادرست است.", "error")

    return render_template("auth/login.html")


@auth_bp.get("/logout")
@login_required
def logout():
    logout_user()
    flash("از حساب خارج شدید.", "success")
    return redirect(url_for("auth.login"))
