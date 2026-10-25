"""Create the first system administrator interactively."""
import getpass

from sqlalchemy.exc import IntegrityError

from app import create_app
from app.extensions import db
from app.models import User

app = create_app()


def main():
    with app.app_context():
        db.create_all()

        username = input("نام کاربری مدیر: ").strip()
        full_name = input("نام کامل مدیر: ").strip()
        password = getpass.getpass("رمز عبور مدیر: ")
        confirm = getpass.getpass("تکرار رمز عبور: ")

        if not username or not full_name:
            raise SystemExit("نام کاربری و نام کامل الزامی است.")
        if len(password) < 12:
            raise SystemExit("رمز عبور باید حداقل ۱۲ نویسه باشد.")
        if password != confirm:
            raise SystemExit("رمزهای عبور یکسان نیستند.")
        if db.session.execute(
            db.select(User.id).where(User.username == username)
        ).scalar_one_or_none():
            raise SystemExit("این نام کاربری قبلاً ثبت شده است.")

        user = User(
            username=username,
            full_name=full_name,
            is_active=True,
            is_system_admin=True,
        )
        user.set_password(password)
        db.session.add(user)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise SystemExit("ساخت حساب انجام نشد؛ نام کاربری را بررسی کنید.")

        print("حساب مدیر ساخته شد. رمز عبور در دیتابیس به‌صورت هش ذخیره شده است.")


if __name__ == "__main__":
    main()
