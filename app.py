import os
import secrets
import string
from functools import wraps

from flask import Flask, render_template, redirect, request, jsonify, url_for, Response, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from khayyam import JalaliDatetime
from sqlalchemy import UniqueConstraint

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.environ.get("SECRET_KEY", "OK2oOkNbUq0iDIct$@*")

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "لطفاً ابتدا وارد شوید."
login_manager.login_message_category = "danger"


# ==================== Models ====================
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    user_level = db.Column(db.Integer, default=0)
    roles = db.relationship("UserRole", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    classes = db.relationship("UserClass", back_populates="user", cascade="all, delete-orphan", lazy="selectin")

    def set_password(self, password):
        self.password = password

    def check_password(self, password):
        return self.password == password

    def has_role(self, role):
        return any(item.role == role for item in self.roles)

    def role_names(self):
        return [item.role for item in self.roles]

    def class_numbers(self):
        return [item.class_number for item in self.classes]

    def can_record_class(self, class_number):
        return self.has_role("recorder") and class_number in self.class_numbers()


class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    user = db.relationship("Users", back_populates="roles")
    __table_args__ = (UniqueConstraint("user_id", "role", name="uq_user_role"),)


class UserClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    class_number = db.Column(db.String(20), nullable=False)
    user = db.relationship("Users", back_populates="classes")
    __table_args__ = (UniqueConstraint("user_id", "class_number", name="uq_user_class"),)


class AbsenceStudent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_number = db.Column(db.String(20), nullable=False)
    absence_student = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(10), nullable=False)
    __table_args__ = (UniqueConstraint("class_number", "date", name="uq_absence_class_date"),)


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(Users, int(user_id))
    except (TypeError, ValueError):
        return None


ROLE_NAMES = {"manager", "staff", "recorder"}


with app.app_context():
    db.create_all()


# ==================== Default Manager ====================
def ensure_default_manager():
    manager = (
        Users.query.join(UserRole, UserRole.user_id == Users.id)
        .filter(UserRole.role == "manager")
        .first()
    )
    if manager:
        return

    username = os.environ.get("DEFAULT_MANAGER_USERNAME", "admin").strip() or "admin"
    password = os.environ.get("DEFAULT_MANAGER_PASSWORD", "admin1234")
    full_name = os.environ.get("DEFAULT_MANAGER_NAME", "مدیر سیستم").strip() or "مدیر سیستم"

    existing = Users.query.filter_by(username=username).first()
    if existing:
        existing.roles.append(UserRole(role="manager"))
        db.session.commit()
        return

    manager = Users(full_name=full_name, username=username, user_level=0)
    manager.set_password(password)
    manager.roles.append(UserRole(role="manager"))
    db.session.add(manager)
    db.session.commit()


with app.app_context():
    ensure_default_manager()


# ==================== Helpers ====================
def today_jalali():
    return str(JalaliDatetime.now().date())


def convert_to_list(absence_student_str):
    if not absence_student_str or absence_student_str == "No Absence Student":
        return []
    return [name.strip() for name in absence_student_str.split("-") if name.strip()]


def normalize_absence_names(value):
    if not isinstance(value, str):
        return None
    names = [name.strip() for name in value.split("-") if name.strip()]
    if len(names) > 16 or any(len(name) > 100 for name in names):
        return None
    return " - ".join(names) if names else "No Absence Student"


def normalize_roles(value):
    if not isinstance(value, list):
        return None
    roles = []
    for role in value:
        if role not in ROLE_NAMES:
            return None
        if role not in roles:
            roles.append(role)
    return roles


def normalize_classes(value):
    if value is None:
        return []
    if isinstance(value, str):
        values = value.replace("،", ",").split(",")
    elif isinstance(value, list):
        values = value
    else:
        return None
    classes = []
    for class_number in values:
        class_number = str(class_number).strip()
        if not class_number:
            continue
        if len(class_number) > 20:
            return None
        if class_number not in classes:
            classes.append(class_number)
    return classes


def role_required(*allowed_roles):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if not any(current_user.has_role(role) for role in allowed_roles):
                return render_template("error.html", status_code=403, e="شما اجازه دسترسی به این بخش را ندارید."), 403
            return view(*args, **kwargs)
        return wrapped
    return decorator


def recorder_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.has_role("recorder") or not current_user.class_numbers():
            return render_template("error.html", status_code=403, e="برای ثبت غیبت باید نقش ثبت‌کننده و حداقل یک کلاس داشته باشید."), 403
        return view(*args, **kwargs)
    return wrapped


def manager_required(view):
    return role_required("manager")(view)


def staff_or_manager_required(view):
    return role_required("staff", "manager")(view)


def requested_class_number(data=None):
    data = data or {}
    class_number = data.get("class_number") or request.args.get("class_number") or request.args.get("class")
    return str(class_number).strip() if class_number else None


def ensure_recording_class(class_number):
    if not class_number:
        return False
    return current_user.can_record_class(class_number)


def user_to_dict(user):
    return {"id": user.id, "fullName": user.full_name, "username": user.username, "roles": user.role_names(), "classNumbers": user.class_numbers()}


# ==================== Pages ====================
@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("با موفقیت خارج شدید.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/editAbsenceStudent")
@recorder_required
def ea_student():
    class_number = requested_class_number()
    if not ensure_recording_class(class_number):
        return redirect(url_for("dashboard"))
    record = AbsenceStudent.query.filter_by(class_number=class_number, date=today_jalali()).first()
    if not record:
        return redirect(url_for("dashboard"))
    return render_template("edit_as.html", absence_student=convert_to_list(record.absence_student), selected_class=class_number)


# ==================== Authentication APIs ====================
@app.route("/api/create_password/<length>")
def create_password(length):
    if not length.isdigit():
        return jsonify(error="مقدار وارد شده معتبر نیست."), 400
    length_int = int(length)
    if not 4 <= length_int <= 64:
        return jsonify(error="طول رمز باید بین 4 تا 64 باشد."), 400
    characters = string.ascii_letters + string.digits
    return jsonify(password="".join(secrets.choice(characters) for _ in range(length_int)))


@app.route("/api/reg_api", methods=["POST"])
def register_api():
    data = request.get_json(silent=True) or {}
    full_name = (data.get("full_name") or "").strip()
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    if not full_name or not username or not password:
        return jsonify(message="نام، نام کاربری و رمز عبور الزامی است.", category="danger"), 400
    if Users.query.filter_by(username=username).first():
        return jsonify(message="این نام کاربری در سیستم وجود دارد.", category="danger"), 409
    new_user = Users(full_name=full_name, username=username, user_level=0)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(message="ثبت نام با موفقیت انجام شد. حساب شما باید توسط مدیر فعال شود.", category="success"), 201


@app.route("/api/login_api", methods=["POST"])
def login_api():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    user = Users.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return Response(status=401)
    login_user(user)
    return Response(status=200)


@app.route("/api/userInfo", methods=["GET"])
@login_required
def user_info():
    return jsonify(id=current_user.id, FullName=current_user.full_name, UserLevel=current_user.user_level, Roles=current_user.role_names(), ClassNumbers=current_user.class_numbers())


# ==================== Absence APIs ====================
@app.route("/api/setAbsenceStudent", methods=["POST"])
@recorder_required
def set_absence_student():
    data = request.get_json(silent=True) or {}
    class_number = requested_class_number(data)
    if not ensure_recording_class(class_number):
        return jsonify(message="این کلاس به شما اختصاص داده نشده است.", category="danger"), 403
    normalized = normalize_absence_names(data.get("absenceStudent", ""))
    if normalized is None:
        return jsonify(message="اطلاعات غیبت معتبر نیست. حداکثر ۱۶ دانش‌آموز مجاز است.", category="danger"), 400
    today = today_jalali()
    existing = AbsenceStudent.query.filter_by(class_number=class_number, date=today).first()
    if existing:
        return jsonify(message="غیبت این کلاس برای امروز قبلاً ثبت شده است.", category="warning"), 409
    db.session.add(AbsenceStudent(class_number=class_number, absence_student=normalized, date=today))
    db.session.commit()
    return jsonify(message="عملیات با موفقیت انجام شد.", category="success"), 201


@app.route("/api/editAbsenceStudent", methods=["POST"])
@recorder_required
def edit_absence_student():
    data = request.get_json(silent=True) or {}
    class_number = requested_class_number(data)
    if not ensure_recording_class(class_number):
        return jsonify(message="این کلاس به شما اختصاص داده نشده است.", category="danger"), 403
    normalized = normalize_absence_names(data.get("absenceStudent", ""))
    if normalized is None:
        return jsonify(message="اطلاعات غیبت معتبر نیست. حداکثر ۱۶ دانش‌آموز مجاز است.", category="danger"), 400
    record = AbsenceStudent.query.filter_by(class_number=class_number, date=today_jalali()).first()
    if not record:
        return jsonify(message="رکوردی پیدا نشد.", category="danger"), 404
    record.absence_student = normalized
    db.session.commit()
    return jsonify(message="عملیات با موفقیت انجام شد.", category="success"), 200


@app.route("/api/isEnterAbsenceStudent", methods=["GET"])
@recorder_required
def is_eas():
    class_number = requested_class_number()
    if not ensure_recording_class(class_number):
        return jsonify(message="این کلاس به شما اختصاص داده نشده است.", category="danger"), 403
    exists = AbsenceStudent.query.filter_by(class_number=class_number, date=today_jalali()).first() is not None
    return jsonify(entered=exists)


@app.route("/api/absenceSummary", methods=["GET"])
@staff_or_manager_required
def absence_summary():
    today = today_jalali()
    records = AbsenceStudent.query.filter_by(date=today).all()
    classes, total_absent = [], 0
    for record in records:
        names = convert_to_list(record.absence_student)
        count = len(names)
        total_absent += count
        classes.append({"classNumber": record.class_number, "absenceCount": count, "students": names})
    classes.sort(key=lambda item: item["classNumber"] or "")
    return jsonify(date=today, totalClasses=len(classes), totalAbsent=total_absent, classes=classes)


# ==================== Manager / User Management APIs ====================
@app.route("/api/users", methods=["GET"])
@manager_required
def list_users():
    return jsonify(users=[user_to_dict(user) for user in Users.query.order_by(Users.id.asc()).all()])


@app.route("/api/users", methods=["POST"])
@manager_required
def create_user():
    data = request.get_json(silent=True) or {}
    full_name = (data.get("full_name") or "").strip()
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    roles = normalize_roles(data.get("roles", []))
    classes = normalize_classes(data.get("class_numbers", data.get("classes", [])))
    if not full_name or not username or not password:
        return jsonify(message="نام، نام کاربری و رمز عبور الزامی است.", category="danger"), 400
    if roles is None or not roles:
        return jsonify(message="حداقل یک نقش انتخاب کنید.", category="danger"), 400
    if classes is None:
        return jsonify(message="لیست کلاس‌ها معتبر نیست.", category="danger"), 400
    if Users.query.filter_by(username=username).first():
        return jsonify(message="این نام کاربری قبلاً ثبت شده است.", category="danger"), 409
    if "recorder" in roles and not classes:
        return jsonify(message="برای نقش معلم / ثبت‌کننده حداقل یک کلاس انتخاب کنید.", category="danger"), 400
    if "recorder" not in roles:
        classes = []
    user = Users(full_name=full_name, username=username, user_level=0)
    user.set_password(password)
    user.roles.extend(UserRole(role=role) for role in roles)
    user.classes.extend(UserClass(class_number=class_number) for class_number in classes)
    db.session.add(user)
    db.session.commit()
    return jsonify(message="کاربر با موفقیت ایجاد شد.", category="success", user=user_to_dict(user)), 201


@app.route("/api/users/<int:user_id>", methods=["PATCH"])
@manager_required
def update_user(user_id):
    user = db.session.get(Users, user_id)
    if not user:
        return jsonify(message="کاربر پیدا نشد.", category="danger"), 404
    data = request.get_json(silent=True) or {}
    full_name = (data.get("full_name") or "").strip()
    username = (data.get("username") or "").strip()
    roles = normalize_roles(data.get("roles")) if "roles" in data else user.role_names()
    classes = normalize_classes(data.get("class_numbers", data.get("classes"))) if ("class_numbers" in data or "classes" in data) else user.class_numbers()
    if not full_name or not username:
        return jsonify(message="نام و نام کاربری الزامی است.", category="danger"), 400
    if roles is None or not roles:
        return jsonify(message="حداقل یک نقش انتخاب کنید.", category="danger"), 400
    if classes is None:
        return jsonify(message="لیست کلاس‌ها معتبر نیست.", category="danger"), 400
    if "recorder" in roles and not classes:
        return jsonify(message="برای نقش معلم / ثبت‌کننده حداقل یک کلاس انتخاب کنید.", category="danger"), 400
    if "recorder" not in roles:
        classes = []
    if Users.query.filter(Users.username == username, Users.id != user.id).first():
        return jsonify(message="این نام کاربری قبلاً ثبت شده است.", category="danger"), 409
    user.full_name, user.username = full_name, username
    if data.get("password") and str(data.get("password")).strip():
        user.set_password(str(data.get("password")).strip())
    user.roles.clear()
    user.classes.clear()
    user.roles.extend(UserRole(role=role) for role in roles)
    user.classes.extend(UserClass(class_number=class_number) for class_number in classes)
    db.session.commit()
    return jsonify(message="اطلاعات کاربر به‌روزرسانی شد.", category="success", user=user_to_dict(user))


@app.route("/api/users/<int:user_id>", methods=["DELETE"])
@manager_required
def delete_user(user_id):
    user = db.session.get(Users, user_id)
    if not user:
        return jsonify(message="کاربر پیدا نشد.", category="danger"), 404
    if user.id == current_user.id:
        return jsonify(message="نمی‌توانید حساب خودتان را حذف کنید.", category="danger"), 400
    db.session.delete(user)
    db.session.commit()
    return jsonify(message="کاربر حذف شد.", category="success")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", status_code=404, e=e), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template("error.html", status_code=403, e=e), 403


@app.errorhandler(500)
def internal_server_error(e):
    db.session.rollback()
    return render_template("error.html", status_code=500, e=e), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=1111)
