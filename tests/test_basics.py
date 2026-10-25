from app.extensions import db
from app.models import User


def test_home_redirects_to_setup_when_empty(client):
    """First visit with no users should go to the setup wizard."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (302, 303)
    assert "/setup" in response.headers["Location"]


def test_setup_page_renders(client):
    response = client.get("/setup/")
    assert response.status_code == 200
    assert "راه‌اندازی اولیه".encode("utf-8") in response.data
    assert "حساب مدیر".encode("utf-8") in response.data


def test_create_admin_via_setup(client, app):
    """Browser-based first-run creates the system admin and logs them in."""
    response = client.post(
        "/setup/",
        data={
            "username": "admin",
            "full_name": "مدیر سیستم",
            "password": "secure-password-12",
            "confirm_password": "secure-password-12",
        },
        follow_redirects=False,
    )
    assert response.status_code in (302, 303)
    assert "/dashboard" in response.headers["Location"]

    with app.app_context():
        user = db.session.execute(
            db.select(User).where(User.username == "admin")
        ).scalar_one()
        assert user.is_system_admin is True
        assert user.check_password("secure-password-12")


def test_home_redirects_to_login_after_setup(client, app):
    with app.app_context():
        user = User(
            username="admin",
            full_name="مدیر سیستم",
            is_active=True,
            is_system_admin=True,
        )
        user.set_password("secure-password-12")
        db.session.add(user)
        db.session.commit()

    response = client.get("/", follow_redirects=False)
    assert response.status_code in (302, 303)
    assert "/auth/login" in response.headers["Location"]


def test_setup_blocked_after_admin_exists(client, app):
    with app.app_context():
        user = User(
            username="admin",
            full_name="مدیر سیستم",
            is_active=True,
            is_system_admin=True,
        )
        user.set_password("secure-password-12")
        db.session.add(user)
        db.session.commit()

    response = client.get("/setup/", follow_redirects=False)
    assert response.status_code in (302, 303)
    assert "/auth/login" in response.headers["Location"]


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"
