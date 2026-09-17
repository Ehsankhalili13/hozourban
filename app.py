import os
import random
import string
from flask import Flask, render_template, redirect, request, flash, session, jsonify, url_for, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from khayyam import JalaliDatetime

app = Flask(__name__)

# کانفیگ‌ها
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "database.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get("SECRET_KEY", "OK2oOkNbUq0iDIct$@*E")

# 1. مقداردهی اولیه پایگاه داده و مدیریت ورود
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "لطفاً ابتدا وارد شوید."
login_manager.login_message_category = "danger"

# 2. مدل‌های دیتابیس (ارث‌بری از UserMixin برای Flask-Login)
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    user_level = db.Column(db.Integer, default=0)
    class_number = db.Column(db.String(20), unique=True)

    def set_password(self, password):
        self.password = password

    def check_password(self, password):
        return self.password == password

class AbsenceStudent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_number = db.Column(db.String(20))
    absence_student = db.Column(db.Text)
    date = db.Column(db.String(10))

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

with app.app_context():
    db.create_all()

# --- توابع کمکی ---
def convert_to_list(absence_student_str):
    if not absence_student_str or absence_student_str == "No Absence Student":
        return []
    return absence_student_str.split("-")

# --- مسیرهای عمومی (General Routes) ---
@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("با موفقیت خارج شدید.", "info")
    return redirect(url_for("login"))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_level == 1:
        return render_template("t_panel.html")
    elif current_user.user_level in [2, 3]:
        return render_template("ss_panel.html")
    else:
        return render_template("401.html"), 401

@app.route("/editAbsenceStudent/")
@login_required
def ea_student():
    if current_user.user_level != 1:
        return render_template("401.html"), 401

    c_num = current_user.class_number
    today = str(JalaliDatetime.now().date())
    as_info = AbsenceStudent.query.filter_by(class_number=c_num, date=today).first()

    if not as_info:
        return redirect(url_for("dashboard"))

    return render_template("edit_as.html", absence_student=convert_to_list(as_info.absence_student))

# ========== API ROUTE ==========
@app.route("/api/create_password/<length>")
def create_password(length):
    if not length.isdigit():
        return jsonify(error="مقدار وارد شده معتبر نیست."), 400
    
    length_int = min(int(length), 64) # محدودسازی طول پسورد
    characters = string.ascii_letters + string.digits
    final_password = "".join(random.choice(characters) for _ in range(length_int))
    return jsonify(password=final_password)

@app.route("/api/reg_api", methods=["POST"])
def register_api():
    data = request.get_json() or {}
    full_name = data.get("full_name")
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify(message="نام کاربری و رمز عبور الزامی است.", category="danger"), 400

    if Users.query.filter_by(full_name=full_name).first():
        return jsonify(message="این نام در سیستم وجود دارد.", category="danger"), 400
    if Users.query.filter_by(username=username).first():
        return jsonify(message="این نام کاربری در سیستم وجود دارد.", category="danger"), 400

    new_user = Users(full_name=full_name, username=username, user_level=0)
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user)
    return jsonify(message="ثبت نام شما موفقیت‌آمیز بود.", category="success")

@app.route("/api/login_api", methods=["POST"])
def login_api():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    user = Users.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        return Response(status=200)
    
    return Response(status=401)

@app.route("/api/userInfo", methods=["POST"])
@login_required
def user_info():
    return jsonify(
        FullName=current_user.full_name,
        UserLevel=current_user.user_level,
        ClassNumber=current_user.class_number
    )

@app.route("/api/setAbsenceStudent", methods=["POST"])
@login_required
def set_absence_student():
    data = request.get_json() or {}
    class_num = data.get("classNumber")
    absence_student = data.get("absenceStudent")
    today = str(JalaliDatetime.now().date())

    s_obj = AbsenceStudent(
        class_number=class_num,
        absence_student=absence_student,
        date=today
    )
    db.session.add(s_obj)
    db.session.commit()

    return jsonify(message="عملیات با موفقیت انجام شد.", category="success")

@app.route("/api/editAbsenceStudent", methods=["POST"])
@login_required
def edit_absence_student():
    data = request.get_json() or {}
    class_num = data.get("classNumber")
    today = str(JalaliDatetime.now().date())
    absence_student = data.get("absenceStudent")

    edit_data = AbsenceStudent.query.filter_by(class_number=class_num, date=today).first()
    if not edit_data:
        return jsonify(message="رکوردی پیدا نشد.", category="danger"), 404

    edit_data.absence_student = "No Absence Student" if not absence_student else absence_student
    db.session.commit()
    
    return jsonify(message="عملیات با موفقیت انجام شد.", category="success")

@app.route("/api/isEnterAbsenceStudent", methods=["POST"])
@login_required
def is_eas():
    data = request.get_json() or {}
    c_num = data.get("ClassNumber")
    today = str(JalaliDatetime.now().date())

    exists = AbsenceStudent.query.filter_by(class_number=c_num, date=today).first()
    status = "Entered" if exists else "Not Enter"
    return jsonify(message=status)


# ========== ERROR HANDLER ==========
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", status_code=404, e=e), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template("error.html", status_code=403, e=e), 403


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=1111)