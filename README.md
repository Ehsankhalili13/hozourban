# 🏫 Attendance Guard (حضوربان)

> A lightweight, modern, and extensible school attendance management system built with Flask.

**فارسی:** [بخش فارسی](#-نسخه-فارسی)

---

## ✨ Features

- 🔐 User authentication with Session and Flask-Login
- 👥 Three main roles:
  - **Manager** — manages users and views absences
  - **School Staff** — views daily absences
  - **Teacher / Recorder** — records and edits absences
- 🧩 Multiple roles per user; one user can have several roles at the same time
- 🏫 Multiple classes per teacher, such as `701`, `702`, and `801`
- 📝 Up to 16 absent students per class per day
- 🚫 Option to record **No Absence**
- ✏️ Edit previously recorded absences
- 📊 Daily absence summary for managers and school staff
- 👤 User creation and deletion by managers
- 🗃️ SQLite for simple local execution
- 🗓️ Jalali date support for attendance records
- 📱 Responsive dashboard for desktop, tablet, and mobile
- 🗑️ Student-name inputs can be removed with a trash button that appears on hover
- 🧹 Local database files are excluded from Git

---

## 🧱 Tech Stack

| Area | Technology |
|---|---|
| Backend | Flask |
| ORM | Flask-SQLAlchemy |
| Authentication | Flask-Login |
| Database | SQLite |
| Date | Khayyam / JalaliDatetime |
| Frontend | HTML / CSS / JavaScript |

---

## 🗂️ Project Structure

```text
attendance-guard/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── static/
│   ├── css/
│   └── js/
└── templates/
    ├── base.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── edit_as.html
    └── error.html
```

> `database.db` is created locally when the application runs and is intentionally excluded from GitHub.

---

## 🚀 Installation & Usage

### 1. Clone the project

```bash
git clone https://github.com/Ehsankhalili13/attendance-guard.git
cd attendance-guard
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:1111
```

---

## 🔑 Default Manager

On the first run, if no user with the **Manager** role exists, the application automatically creates one.

Default credentials:

```text
Username: admin
Password: admin1234
Name: System Manager
```

These values can be overridden before running the application with:

```text
DEFAULT_MANAGER_USERNAME
DEFAULT_MANAGER_PASSWORD
DEFAULT_MANAGER_NAME
```

For a real deployment, change the default password and use secure environment variables.

---

## 👨‍🏫 Teacher & Class Assignment

A teacher is not limited to a single class. A manager can assign multiple classes to the same teacher, for example:

```text
701
702
801
```

After logging in, the teacher selects one of the assigned classes and records attendance for that class.

Each class has only one absence record per day, preventing duplicate records for the same class and date.

---

## 👥 Roles

### Manager

- View daily absences
- Create users
- Assign multiple roles to a user
- Assign multiple classes to teachers
- Delete users

### School Staff

- View daily absences

### Teacher / Recorder

- Select an assigned class
- Record absences
- Record **No Absence**
- Edit the absence record for the selected class

---

## 🔑 Multi-Role Users

Roles are stored independently, so a user can have a combination such as:

```text
Manager + School Staff + Teacher / Recorder
```

This structure also makes adding new roles easier in the future.

---

## 🗄️ Database

The application uses SQLite. The database is created locally as:

```text
database.db
```

It is a runtime file and is intentionally not stored on GitHub.

To start with a clean database, delete the local `database.db` and run the application again. Required tables will be created automatically with `db.create_all()`.

---

## 📱 Responsive UI

The dashboard is optimized for:

- Desktop
- Laptop
- Tablet
- Mobile

In the absence-recording section, hovering over a student-name input reveals a delete button for that input. On touch devices, the delete control remains accessible because hover is not available.

---

## ⚠️ Security Note

This project is currently designed for **local / localhost use** and passwords are stored as Plain Text by design.

If the project is deployed to a public server, authentication and password storage should be redesigned using secure password hashing and `SECRET_KEY` should be provided through a secure environment variable.

---

## 🛠️ Project Status

The project is under active development. Possible future features include:

- Grade and field management
- Student lists for each class
- Daily and monthly reports
- Excel / PDF export
- Attendance calendar
- Advanced statistics dashboard
- Teacher weekly schedule management

---

## 📄 License

All rights reserved. Use of the source code is permitted only with the developer's permission.

---

# 🇮🇷 نسخه فارسی

> یک سیستم سبک، مدرن و قابل توسعه برای **مدیریت کاربران و ثبت حضور و غیاب مدرسه** با Flask.

## ✨ امکانات

- 🔐 ورود و خروج کاربران با Session و Flask-Login
- 👥 سه نقش اصلی:
  - **مدیر** — مدیریت کاربران و مشاهده غیبت‌ها
  - **کارشناس مدرسه** — مشاهده غیبت‌ها
  - **معلم / ثبت‌کننده** — ثبت و ویرایش غیبت
- 🧩 پشتیبانی از چند نقش برای یک کاربر
- 🏫 پشتیبانی از چند کلاس برای هر معلم
- 📝 ثبت حداکثر ۱۶ دانش‌آموز غایب برای هر کلاس در هر روز
- 🚫 امکان ثبت «بدون غیبت»
- ✏️ امکان ویرایش غیبت ثبت‌شده
- 📊 نمایش خلاصه غیبت‌های روز برای مدیر و کارشناس
- 👤 ساخت و حذف کاربران توسط مدیر
- 🗃️ استفاده از SQLite برای اجرای ساده روی سیستم محلی
- 🗓️ استفاده از تاریخ جلالی برای ثبت غیبت
- 📱 داشبورد ریسپانسیو برای موبایل، تبلت و دسکتاپ
- 🗑️ نمایش سطل زباله هنگام Hover روی ورودی نام دانش‌آموز برای حذف سریع آن
- 🧹 عدم نگهداری دیتابیس محلی در Git

## 🧱 تکنولوژی‌ها

| بخش | تکنولوژی |
|---|---|
| Backend | Flask |
| ORM | Flask-SQLAlchemy |
| Authentication | Flask-Login |
| Database | SQLite |
| Date | Khayyam / JalaliDatetime |
| Frontend | HTML / CSS / JavaScript |

## 🗂️ ساختار پروژه

```text
attendance-guard/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── static/
│   ├── css/
│   └── js/
└── templates/
    ├── base.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── edit_as.html
    └── error.html
```

`database.db` هنگام اجرای برنامه به‌صورت محلی ساخته می‌شود و به دلیل قرار داشتن در `.gitignore` وارد GitHub نمی‌شود.

## 🚀 نصب و اجرا

### ۱. دریافت پروژه

```bash
git clone https://github.com/Ehsankhalili13/attendance-guard.git
cd attendance-guard
```

### ۲. ساخت محیط مجازی

در Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### ۳. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

### ۴. اجرای برنامه

```bash
python app.py
```

سپس مرورگر را باز کرده و وارد آدرس زیر شوید:

```text
http://127.0.0.1:1111
```

## 🔑 مدیر پیش‌فرض

در اولین اجرای برنامه، اگر هیچ کاربری با نقش **مدیر** وجود نداشته باشد، یک مدیر به‌صورت خودکار ساخته می‌شود.

```text
نام کاربری: admin
رمز عبور: admin1234
نام: مدیر سیستم
```

این مقادیر را می‌توان قبل از اجرای برنامه با متغیرهای محیطی زیر تغییر داد:

```text
DEFAULT_MANAGER_USERNAME
DEFAULT_MANAGER_PASSWORD
DEFAULT_MANAGER_NAME
```

## 👨‍🏫 تخصیص کلاس به معلم

هر معلم می‌تواند چند کلاس داشته باشد. برای مثال مدیر می‌تواند کلاس‌های زیر را به یک معلم اختصاص دهد:

```text
701
702
801
```

معلم پس از ورود، کلاس موردنظر را از بین کلاس‌های اختصاص‌یافته انتخاب کرده و غیبت همان کلاس را ثبت می‌کند.

برای هر کلاس در هر روز فقط یک رکورد غیبت ثبت می‌شود.

## 👥 نقش‌ها

### مدیر

- مشاهده غیبت‌های روز
- ایجاد کاربر
- تعیین چند نقش برای یک کاربر
- تعیین چند کلاس برای معلم
- حذف کاربران

### کارشناس مدرسه

- مشاهده غیبت‌های روز

### معلم / ثبت‌کننده

- انتخاب کلاس اختصاص‌یافته
- ثبت غیبت
- ثبت «بدون غیبت»
- ویرایش غیبت همان کلاس

## 🔑 چندنقشی بودن کاربران

یک کاربر می‌تواند هم‌زمان چند نقش داشته باشد، برای مثال:

```text
مدیر + کارشناس مدرسه + معلم / ثبت‌کننده
```

## 🗄️ دیتابیس

برنامه از SQLite استفاده می‌کند و فایل زیر در محیط محلی ساخته می‌شود:

```text
database.db
```

این فایل عمداً در GitHub قرار نمی‌گیرد.

برای ساخت یک دیتابیس تمیز، کافی است `database.db` محلی را حذف کرده و برنامه را دوباره اجرا کنید.

## 📱 رابط کاربری

داشبورد برای دسکتاپ، لپ‌تاپ، تبلت و موبایل ریسپانسیو شده است.

در بخش ثبت غیبت، با Hover روی ورودی نام دانش‌آموز، دکمه سطل زباله ظاهر می‌شود و همان ورودی را حذف می‌کند.

## ⚠️ نکته امنیتی

این پروژه در حال حاضر برای **استفاده محلی / localhost** طراحی شده و رمزها عمداً به‌صورت Plain Text ذخیره می‌شوند.

برای استفاده روی سرور عمومی، باید ذخیره رمزها با روش امن مانند Password Hashing انجام شود و `SECRET_KEY` نیز از یک متغیر محیطی امن دریافت شود.

## 🛠️ وضعیت پروژه

پروژه در حال توسعه است و در آینده قابلیت‌هایی مانند گزارش‌گیری روزانه و ماهانه، خروجی Excel / PDF، تقویم حضور و غیاب، مدیریت لیست دانش‌آموزان و داشبورد آماری می‌توانند به آن اضافه شوند.

## 📄 License

تمام حقوق مادی و معنوی محفوظ است. استفاده از سورس کد با اجازه توسعه‌دهنده مجاز است.
