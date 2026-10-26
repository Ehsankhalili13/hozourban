"""School structure models: schools, academic years, class groups."""
from datetime import date

from app.extensions import db
from app.models.identity import utc_now


class School(db.Model):
    __tablename__ = "schools"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(40), unique=True, nullable=True, index=True)
    address = db.Column(db.String(300), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    academic_years = db.relationship(
        "AcademicYear", back_populates="school", cascade="all, delete-orphan"
    )
    class_groups = db.relationship(
        "ClassGroup", back_populates="school", cascade="all, delete-orphan"
    )
    students = db.relationship(
        "Student", back_populates="school", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<School {self.name}>"


class AcademicYear(db.Model):
    __tablename__ = "academic_years"
    __table_args__ = (
        db.UniqueConstraint("school_id", "title", name="uq_school_year_title"),
    )

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey("schools.id"), nullable=False, index=True)
    title = db.Column(db.String(40), nullable=False)  # e.g. 1404-1405
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    is_current = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)

    school = db.relationship("School", back_populates="academic_years")
    class_groups = db.relationship(
        "ClassGroup", back_populates="academic_year", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<AcademicYear {self.title}>"


class ClassGroup(db.Model):
    """A class section within a school/year, e.g. پایه هفتم — الف."""
    __tablename__ = "class_groups"
    __table_args__ = (
        db.UniqueConstraint(
            "school_id", "academic_year_id", "grade", "section",
            name="uq_class_group_scope",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey("schools.id"), nullable=False, index=True)
    academic_year_id = db.Column(
        db.Integer, db.ForeignKey("academic_years.id"), nullable=False, index=True
    )
    name = db.Column(db.String(120), nullable=False)  # display name
    grade = db.Column(db.String(40), nullable=False)  # پایه / مقطع
    section = db.Column(db.String(20), nullable=True)  # الف، ب، ...
    capacity = db.Column(db.Integer, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)

    school = db.relationship("School", back_populates="class_groups")
    academic_year = db.relationship("AcademicYear", back_populates="class_groups")
    enrollments = db.relationship(
        "Enrollment", back_populates="class_group", cascade="all, delete-orphan"
    )
    teacher_assignments = db.relationship(
        "TeacherAssignment", back_populates="class_group", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ClassGroup {self.name}>"
