import os
import sys

# let this script find the "app" package in the project folder above it
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    name = input("Admin name: ").strip()
    email = input("Admin email: ").strip().lower()
    password = input("Admin password (min 6 characters): ")

    if User.query.filter_by(email=email).first():
        print("That email already exists.")
    elif len(password) < 6:
        print("Password too short.")
    else:
        admin = User(name=name, email=email, role="admin")
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print("Admin created.")