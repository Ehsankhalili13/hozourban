from app.models.identity import Permission, Role, User, UserRole
from app.models.school import AcademicYear, ClassGroup, School
from app.models.people import Enrollment, Student, TeacherAssignment
from app.models.attendance import AttendanceRecord, AttendanceSession

__all__ = [
    "User",
    "Role",
    "Permission",
    "UserRole",
    "School",
    "AcademicYear",
    "ClassGroup",
    "Student",
    "Enrollment",
    "TeacherAssignment",
    "AttendanceSession",
    "AttendanceRecord",
]
