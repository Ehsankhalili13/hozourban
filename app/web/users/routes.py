from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.core.permissions.decorators import permission_required
from app.extensions import db
from app.models import ClassGroup, Enrollment, School, Student
from app.web.users import users_bp


@users_bp.route("/")
@login_required
@permission_required("student.view")
def list_students():
    students = db.session.execute(
        db.select(Student)
        .where(Student.is_active.is_(True))
        .order_by(Student.last_name, Student.first_name)
    ).scalars().all()
    return render_template("users/students_list.html", students=students)


@users_bp.route("/new", methods=["GET", "POST"])
@login_required
@permission_required("student.manage")
def create_student():
    schools = db.session.execute(
        db.select(School).where(School.is_active.is_(True)).order_by(School.name)
    ).scalars().all()
    classes = db.session.execute(
        db.select(ClassGroup).where(ClassGroup.is_active.is_(True)).order_by(ClassGroup.name)
    ).scalars().all()

    if request.method == "POST":
        school_id = request.form.get("school_id", type=int)
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        student_code = request.form.get("student_code", "").strip() or None
        national_id = request.form.get("national_id", "").strip() or None
        gender = request.form.get("gender", "").strip() or None
        class_group_id = request.form.get("class_group_id", type=int)

        if not school_id or not first_name or not last_name:
            flash("مدرسه، نام و نام خانوادگی الزامی است.", "error")
            return render_template(
                "users/student_form.html", schools=schools, classes=classes
            )

        student = Student(
            school_id=school_id,
            first_name=first_name,
            last_name=last_name,
            student_code=student_code,
            national_id=national_id,
            gender=gender,
            is_active=True,
        )
        db.session.add(student)
        db.session.flush()

        if class_group_id:
            db.session.add(
                Enrollment(
                    student_id=student.id,
                    class_group_id=class_group_id,
                    is_active=True,
                )
            )

        db.session.commit()
        flash("دانش‌آموز ثبت شد.", "success")
        return redirect(url_for("users.list_students"))

    return render_template(
        "users/student_form.html", schools=schools, classes=classes
    )
