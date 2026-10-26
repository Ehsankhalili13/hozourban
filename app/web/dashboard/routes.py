from datetime import date

from flask import render_template
from flask_login import current_user, login_required

from app.extensions import db
from app.models import AttendanceSession, ClassGroup, School, Student
from app.web.dashboard import dashboard_bp


@dashboard_bp.route("/")
@login_required
def index():
    schools_count = db.session.execute(db.select(db.func.count(School.id))).scalar() or 0
    classes_count = db.session.execute(db.select(db.func.count(ClassGroup.id))).scalar() or 0
    students_count = db.session.execute(db.select(db.func.count(Student.id))).scalar() or 0
    today_sessions = db.session.execute(
        db.select(db.func.count(AttendanceSession.id)).where(
            AttendanceSession.session_date == date.today()
        )
    ).scalar() or 0

    recent_sessions = db.session.execute(
        db.select(AttendanceSession)
        .order_by(AttendanceSession.session_date.desc(), AttendanceSession.id.desc())
        .limit(8)
    ).scalars().all()

    return render_template(
        "dashboard/index.html",
        user=current_user,
        stats={
            "schools": schools_count,
            "classes": classes_count,
            "students": students_count,
            "today_sessions": today_sessions,
        },
        recent_sessions=recent_sessions,
    )
