"""Bootstrap default roles and permissions."""
from app.extensions import db
from app.models import Permission, Role

# (code, description)
DEFAULT_PERMISSIONS = [
    ("school.manage", "مدیریت مدارس"),
    ("school.view", "مشاهده مدارس"),
    ("year.manage", "مدیریت سال تحصیلی"),
    ("class.manage", "مدیریت کلاس‌ها"),
    ("class.view", "مشاهده کلاس‌ها"),
    ("student.manage", "مدیریت دانش‌آموزان"),
    ("student.view", "مشاهده دانش‌آموزان"),
    ("attendance.take", "ثبت حضور و غیاب"),
    ("attendance.view", "مشاهده حضور و غیاب"),
    ("attendance.report", "گزارش حضور و غیاب"),
    ("user.manage", "مدیریت کاربران"),
    ("role.manage", "مدیریت نقش‌ها"),
]

# role_code -> (title, list of permission codes)
DEFAULT_ROLES = {
    "system_admin": (
        "مدیر سیستم",
        [p[0] for p in DEFAULT_PERMISSIONS],
    ),
    "school_admin": (
        "مدیر مدرسه",
        [
            "school.view",
            "year.manage",
            "class.manage",
            "class.view",
            "student.manage",
            "student.view",
            "attendance.take",
            "attendance.view",
            "attendance.report",
            "user.manage",
        ],
    ),
    "teacher": (
        "معلم",
        [
            "class.view",
            "student.view",
            "attendance.take",
            "attendance.view",
        ],
    ),
    "viewer": (
        "مشاهده‌گر",
        [
            "school.view",
            "class.view",
            "student.view",
            "attendance.view",
            "attendance.report",
        ],
    ),
}


def ensure_roles_and_permissions() -> None:
    """Idempotently create default permissions and roles."""
    perm_by_code: dict[str, Permission] = {}
    for code, description in DEFAULT_PERMISSIONS:
        perm = db.session.execute(
            db.select(Permission).where(Permission.code == code)
        ).scalar_one_or_none()
        if not perm:
            perm = Permission(code=code, description=description)
            db.session.add(perm)
        else:
            perm.description = description
        perm_by_code[code] = perm

    db.session.flush()

    for role_code, (title, perm_codes) in DEFAULT_ROLES.items():
        role = db.session.execute(
            db.select(Role).where(Role.code == role_code)
        ).scalar_one_or_none()
        if not role:
            role = Role(code=role_code, title=title)
            db.session.add(role)
            db.session.flush()
        else:
            role.title = title

        desired = {perm_by_code[c] for c in perm_codes if c in perm_by_code}
        role.permissions = list(desired)

    db.session.commit()
