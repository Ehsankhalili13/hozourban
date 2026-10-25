"""Create the initial database tables.

Development/bootstrap convenience only. Use Flask-Migrate for schema changes
after the initial project setup.
"""
from app import create_app
from app.extensions import db
from app import models  # noqa: F401

app = create_app()

with app.app_context():
    db.create_all()
    print("ساختار اولیه دیتابیس آماده شد.")
