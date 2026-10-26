from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.core.permissions.decorators import permission_required
from app.extensions import db
from app.models import AcademicYear, School
from app.web.school import school_bp


@school_bp.route("/")
@login_required
@permission_required("school.view")
def list_schools():
    schools = db.session.execute(
        db.select(School).order_by(School.name)
    ).scalars().all()
    return render_template("school/list.html", schools=schools)


@school_bp.route("/new", methods=["GET", "POST"])
@login_required
@permission_required("school.manage")
def create_school():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        code = request.form.get("code", "").strip() or None
        address = request.form.get("address", "").strip() or None
        year_title = request.form.get("year_title", "").strip()

        if not name:
            flash("نام مدرسه الزامی است.", "error")
            return render_template("school/form.html", school=None)

        school = School(name=name, code=code, address=address, is_active=True)
        db.session.add(school)
        db.session.flush()

        if year_title:
            year = AcademicYear(
                school_id=school.id,
                title=year_title,
                is_current=True,
            )
            db.session.add(year)

        db.session.commit()
        flash("مدرسه با موفقیت ثبت شد.", "success")
        return redirect(url_for("school.list_schools"))

    return render_template("school/form.html", school=None)


@school_bp.route("/<int:school_id>")
@login_required
@permission_required("school.view")
def detail_school(school_id):
    school = db.get_or_404(School, school_id)
    years = db.session.execute(
        db.select(AcademicYear)
        .where(AcademicYear.school_id == school_id)
        .order_by(AcademicYear.is_current.desc(), AcademicYear.title.desc())
    ).scalars().all()
    return render_template("school/detail.html", school=school, years=years)


@school_bp.route("/<int:school_id>/years/new", methods=["POST"])
@login_required
@permission_required("year.manage")
def add_year(school_id):
    school = db.get_or_404(School, school_id)
    title = request.form.get("title", "").strip()
    is_current = request.form.get("is_current") == "on"
    if not title:
        flash("عنوان سال تحصیلی الزامی است.", "error")
        return redirect(url_for("school.detail_school", school_id=school.id))

    if is_current:
        for y in school.academic_years:
            y.is_current = False

    year = AcademicYear(school_id=school.id, title=title, is_current=is_current)
    db.session.add(year)
    db.session.commit()
    flash("سال تحصیلی اضافه شد.", "success")
    return redirect(url_for("school.detail_school", school_id=school.id))
