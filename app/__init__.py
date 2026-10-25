from pathlib import Path

from flask import Flask, jsonify, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy import text

from config import Config
from app.extensions import db, migrate, login_manager, csrf


def create_app(config_object=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)

    # SQLite file lives in instance/, not in the public source tree.
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "برای ادامه، ابتدا وارد حساب خود شوید."

    # Import models so Flask-Migrate can discover metadata.
    from app.models import User, Role, Permission  # noqa: F401
    from app.web.auth import auth_bp
    from app.web.setup import setup_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(setup_bp)

    @app.get("/dashboard")
    @login_required
    def dashboard():
        return jsonify(
            page="dashboard",
            user={"username": current_user.username, "full_name": current_user.full_name},
            message="پنل اولیه؛ امکانات مدیریتی در مراحل بعد اضافه می‌شوند.",
        )

    @app.get("/health")
    def health():
        # A small readiness check, not an operational monitoring endpoint.
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify(status="ok", service="hozourban")
        except Exception:
            # Tables may not exist yet during first-run.
            return jsonify(status="ok", service="hozourban", note="database not initialized")

    @app.get("/")
    def index():
        """First-run: send to setup wizard. Afterwards: login or dashboard."""
        from app.web.setup.routes import needs_setup, ensure_tables

        try:
            ensure_tables()
            if needs_setup():
                return redirect(url_for("setup.index"))
        except Exception:
            # If anything goes wrong checking setup, still try the wizard.
            return redirect(url_for("setup.index"))

        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return redirect(url_for("auth.login"))

    return app
