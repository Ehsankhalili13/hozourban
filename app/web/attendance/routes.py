from datetime import date, datetime

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.core.permissions.decorators import permission_required
from app.extensions import db
from app.models import (
    AttendanceRecord,
    AttendanceSession,
    ClassGroup,
    Enrollment,
)
from app.models.attendance import ATTENDANCE_STATUSES
from app.web.attendance import attendance_bp


@attendance_bp.route("/")
@login_required
@permission_required("attendance.view")
def index():
    classes = db.session.execute(
        db.select(ClassGroup)
        .where(ClassGroup.is_active.is_(True))
        .order_by(ClassGroup.name)
    ).scalars().all()
    recent = db.session.execute(
        db.select(AttendanceSession)
        .order_by(AttendanceSession.session_date.desc(), AttendanceSession.id.desc())
        .limit(15)
    ).scalars().all()
    return render_template(
        "attendance/index.html",
        classes=classes,
        recent=recent,
        today=date.today().isoformat(),
    )


@attendance_bp.route("/take/<int:class_id>", methods=["GET", "POST"])
@login_required
@permission_required("attendance.take")
def take(class_id):
    cg = db.get_or_404(ClassGroup, class_id)
    students = [
        e.student
        for e in cg.enrollments
        if e.is_active and e.student.is_active
    ]
    students.sort(key=lambda s: (s.last_name, s.first_name))

    session_date_str = request.values.get("session_date") or date.today().isoformat()
    period = request.values.get("period", "").strip() or None

    try:
        session_date = date.fromisoformat(session_date_str)
    except ValueError:
        session_date = date.today()
        session_date_str = session_date.isoformat()

    existing = db.session.execute(
        db.select(AttendanceSession).where(
            AttendanceSession.class_group_id == class_id,
            AttendanceSession.session_date == session_date,
            AttendanceSession.period == period,
        )
    ).scalar_one_or_none()

    if request.method == "POST":
        if not students:
            flash("این کلاس دانش‌آموز فعالی ندارد.", "error")
            return redirect(url_for("attendance.take", class_id=class_id))

        if existing is None:
            existing = AttendanceSession(
                class_group_id=class_id,
                session_date=session_date,
                period=period,
                taken_by_id=current_user.id,
            )
            db.session.add(existing)
            db.session.flush()
        else:
            existing.taken_by_id = current_user.id
            existing.updated_at = datetime.now().astimezone()

        # Clear previous marks for re-save simplicity
        for rec in list(existing.records):
            db.session.delete(rec)
        db.session.flush()

        for student in students:
            status = request.form.get(f"status_{student.id}", "present")
            if status not in ATTENDANCE_STATUSES:
                status = "present"
            note = request.form.get(f"note_{student.id}", "").strip() or None
            db.session.add(
                AttendanceRecord(
                    session_id=existing.id,
                    student_id=student.id,
                    status=status,
                    note=note,
                )
            )

        db.session.commit()
        flash("حضور و غیاب با موفقیت ذخیره شد.", "success")
        return redirect(url_for("attendance.view_session", session_id=existing.id))

    # Prefill from existing session
    marks = {}
    if existing:
        for r in existing.records:
            marks[r.student_id] = r

    return render_template(
        "attendance/take.html",
        class_group=cg,
        students=students,
        session_date=session_date_str,
        period=period or "",
        marks=marks,
        statuses=ATTENDANCE_STATUSES,
        existing=existing,
    )


@attendance_bp.route("/session/<int:session_id>")
@login_required
@permission_required("attendance.view")
def view_session(session_id):
    session = db.get_or_404(AttendanceSession, session_id)
    records = sorted(
        session.records,
        key=lambda r: (r.student.last_name, r.student.first_name),
    )
    summary = session.summary()
    return render_template(
        "attendance/session.html",
        session=session,
        records=records,
        summary=summary,
    )
