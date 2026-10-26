from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.core.permissions.decorators import permission_required
from app.extensions import db
from app.models import AcademicYear, ClassGroup, School
from app.web.academics import academics_bp


@academics_bp.route("/")
@login_required
@permission_required("class.view")
def list_classes():
    classes = db.session.execute(
        db.select(ClassGroup)
        .where(ClassGroup.is_active.is_(True))
        .order_by(ClassGroup.school_id, ClassGroup.grade, ClassGroup.section)
    ).scalars().all()
    return render_template("academics/list.html", classes=classes)


@academics_bp.route("/new", methods=["GET", "POST"])
@login_required
@permission_required("class.manage")
def create_class():
    schools = db.session.execute(
        db.select(School).where(School.is_active.is_(True)).order_by(School.name)
    ).scalars().all()
    years = db.session.execute(
        db.select(AcademicYear).order_by(AcademicYear.is_current.desc(), AcademicYear.title.desc())
    ).scalars().all()

    if request.method == "POST":
        school_id = request.form.get("school_id", type=int)
        year_id = request.form.get("academic_year_id", type=int)
        name = request.form.get("name", "").strip()
        grade = request.form.get("grade", "").strip()
        section = request.form.get("section", "").strip() or None
        capacity = request.form.get("capacity", type=int)

        if not all([school_id, year_id, name, grade]):
            flash("فیلدهای ضروری را پر کنید.", "error")
            return render_template(
                "academics/form.html", schools=schools, years=years, class_group=None
            )

        cg = ClassGroup(
            school_id=school_id,
            academic_year_id=year_id,
            name=name,
            grade=grade,
            section=section,
            capacity=capacity,
            is_active=True,
        )
        db.session.add(cg)
        db.session.commit()
        flash("کلاس ثبت شد.", "success")
        return redirect(url_for("academics.list_classes"))

    return render_template(
        "academics/form.html", schools=schools, years=years, class_group=None
    )


@academics_bp.route("/<int:class_id>")
@login_required
@permission_required("class.view")
def detail_class(class_id):
    cg = db.get_or_404(ClassGroup, class_id)
    students = [
        e.student
        for e in cg.enrollments
        if e.is_active and e.student.is_active
    ]
    students.sort(key=lambda s: (s.last_name, s.first_name))
    return render_template("academics/detail.html", class_group=cg, students=students)
