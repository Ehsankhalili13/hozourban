"""Attendance session and per-student records."""
from datetime import date, datetime, timezone

from app.extensions import db
from app.models.identity import utc_now


# Allowed status codes for a single attendance mark
ATTENDANCE_STATUSES = ("present", "absent", "late", "excused")


class AttendanceSession(db.Model):
    """One attendance taking for a class on a specific date (optionally period)."""
    __tablename__ = "attendance_sessions"
    __table_args__ = (
        db.UniqueConstraint(
            "class_group_id", "session_date", "period",
            name="uq_attendance_session",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    class_group_id = db.Column(
        db.Integer, db.ForeignKey("class_groups.id"), nullable=False, index=True
    )
    session_date = db.Column(db.Date, nullable=False, index=True)
    period = db.Column(db.String(40), nullable=True)  # e.g. morning / زنگ ۱
    taken_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    notes = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    class_group = db.relationship("ClassGroup", backref=db.backref("attendance_sessions", lazy="dynamic"))
    taken_by = db.relationship("User", foreign_keys=[taken_by_id])
    records = db.relationship(
        "AttendanceRecord",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    def summary(self) -> dict:
        counts = {s: 0 for s in ATTENDANCE_STATUSES}
        for r in self.records:
            if r.status in counts:
                counts[r.status] += 1
        return counts


class AttendanceRecord(db.Model):
    """Single student's mark within an attendance session."""
    __tablename__ = "attendance_records"
    __table_args__ = (
        db.UniqueConstraint("session_id", "student_id", name="uq_session_student"),
    )

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(
        db.Integer, db.ForeignKey("attendance_sessions.id"), nullable=False, index=True
    )
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default="present")
    note = db.Column(db.String(200), nullable=True)
    marked_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)

    session = db.relationship("AttendanceSession", back_populates="records")
    student = db.relationship("Student", back_populates="attendance_records")
