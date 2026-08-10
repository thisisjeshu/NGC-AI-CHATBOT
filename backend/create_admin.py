import getpass

from backend.database import SessionLocal
from backend.models import AdminUser
from backend.auth import hash_password


def create_admin():

    db = SessionLocal()

    try:
        username = input("Admin username: ").strip()
        email = input("Admin email: ").strip()
        password = getpass.getpass("Admin password: ")

        existing = (
            db.query(AdminUser)
            .filter(AdminUser.username == username)
            .first()
        )

        if existing:
            print("Admin username already exists.")
            return

        admin = AdminUser(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role="admin",
            is_active=True
        )

        db.add(admin)
        db.commit()

        print("Admin account created successfully!")

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()