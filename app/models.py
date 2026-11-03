from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="student")  # "student" or "admin"
    profile = db.relationship("Profile", backref="user", uselist=False,
                              cascade="all, delete-orphan")
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "admin"

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    location = db.Column(db.String(100))
    gpa = db.Column(db.Float)                  # out of 4.0
    institution = db.Column(db.String(150))    # university / college
    degree_level = db.Column(db.String(30))    # +2, Bachelor, Master, PhD
    course = db.Column(db.String(150))
    field_of_study = db.Column(db.String(100))
    nationality = db.Column(db.String(50), default="Nepali")
    income = db.Column(db.Integer)             # yearly family income (NPR)
    interests = db.Column(db.String(255))