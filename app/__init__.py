from pathlib import Path

from flask import Flask, jsonify, redirect, url_for
from flask_login import current_user
from sqlalchemy import text

from config import Config
from app.extensions import db, migrate, login_manager, csrf


def create_app(config_object=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "برای ادامه، ابتدا وارد حساب خود شوید."

    # Import models so metadata is registered.
    from app import models  # noqa: F401

    from app.web.auth import auth_bp
    from app.web.setup import setup_bp
    from app.web.dashboard import dashboard_bp
    from app.web.school import school_bp
    from app.web.academics import academics_bp
    from app.web.users import users_bp
    from app.web.attendance import attendance_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(setup_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(school_bp)
    app.register_blueprint(academics_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(attendance_bp)

    @app.get("/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify(status="ok", service="hozourban")
        except Exception:
            return jsonify(status="ok", service="hozourban", note="database not initialized")

    @app.get("/")
    def index():
        from app.web.setup.routes import needs_setup, ensure_tables

        try:
            ensure_tables()
            if needs_setup():
                return redirect(url_for("setup.index"))
        except Exception:
            return redirect(url_for("setup.index"))

        if current_user.is_authenticated:
            return redirect(url_for("dashboard.index"))
        return redirect(url_for("auth.login"))

    @app.errorhandler(403)
    def forbidden(_err):
        return (
            "<h1>دسترسی مجاز نیست</h1><p><a href='/dashboard/'>بازگشت به داشبورد</a></p>",
            403,
        )

    return app
