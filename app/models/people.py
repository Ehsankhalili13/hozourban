"""Students, enrollments, and teacher assignments."""
from app.extensions import db
from app.models.identity import utc_now


class Student(db.Model):
    __tablename__ = "students"
    __table_args__ = (
        db.UniqueConstraint("school_id", "student_code", name="uq_school_student_code"),
    )

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey("schools.id"), nullable=False, index=True)
    student_code = db.Column(db.String(40), nullable=True, index=True)  # شماره دانش‌آموزی
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    national_id = db.Column(db.String(20), nullable=True, index=True)
    birth_date = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)  # male / female / other
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    school = db.relationship("School", back_populates="students")
    enrollments = db.relationship(
        "Enrollment", back_populates="student", cascade="all, delete-orphan"
    )
    attendance_records = db.relationship(
        "AttendanceRecord", back_populates="student", cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def __repr__(self) -> str:
        return f"<Student {self.full_name}>"


class Enrollment(db.Model):
    """Student membership in a class group for a given year."""
    __tablename__ = "enrollments"
    __table_args__ = (
        db.UniqueConstraint("student_id", "class_group_id", name="uq_student_class"),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False, index=True)
    class_group_id = db.Column(
        db.Integer, db.ForeignKey("class_groups.id"), nullable=False, index=True
    )
    enrolled_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    student = db.relationship("Student", back_populates="enrollments")
    class_group = db.relationship("ClassGroup", back_populates="enrollments")


class TeacherAssignment(db.Model):
    """Links a user (teacher) to a class group, optionally as primary teacher."""
    __tablename__ = "teacher_assignments"
    __table_args__ = (
        db.UniqueConstraint("user_id", "class_group_id", name="uq_teacher_class"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    class_group_id = db.Column(
        db.Integer, db.ForeignKey("class_groups.id"), nullable=False, index=True
    )
    is_primary = db.Column(db.Boolean, nullable=False, default=True)
    assigned_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)

    user = db.relationship("User", backref=db.backref("teacher_assignments", lazy="dynamic"))
    class_group = db.relationship("ClassGroup", back_populates="teacher_assignments")
