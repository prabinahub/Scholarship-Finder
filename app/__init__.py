from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from .sample_data import SCHOLARSHIPS

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message = "Please log in first."

LEVELS = ["+2", "Bachelor", "Master", "PhD"]
FIELDS = ["IT", "Engineering", "Science", "Medicine", "Management",
          "Education", "Humanities", "Law", "Agriculture", "Other"]


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from . import models  # noqa: F401
        db.create_all()

    from .models import User, Profile

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    def home_for(user):
        return url_for("admin_home") if user.is_admin else url_for("dashboard")

    @app.route("/")
    def home():
        if current_user.is_authenticated:
            return redirect(home_for(current_user))
        return render_template("index.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            name = request.form["name"].strip()
            email = request.form["email"].strip().lower()
            password = request.form["password"]

            if User.query.filter_by(email=email).first():
                flash("That email is already registered.", "danger")
            else:
                user = User(name=name, email=email, role="student")
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                flash("Account created. You can now log in.", "success")
                return redirect(url_for("login"))
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(home_for(current_user))
        if request.method == "POST":
            email = request.form["email"].strip().lower()
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(request.form["password"]):
                login_user(user)
                return redirect(home_for(user))
            flash("Wrong email or password.", "danger")
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("home"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        if current_user.is_admin:
            return redirect(url_for("admin_home"))

        p = current_user.profile
        has_profile = bool(p and p.degree_level)
        q = request.args.get("q", "").strip().lower()
        level = request.args.get("level", "")
        field = request.args.get("field", "")
        searching = bool(q or level or field)

        results = []
        for s in SCHOLARSHIPS:
            if q and q not in (s["title"] + " " + s["description"]).lower():
                continue
            if level and level not in s["degree_level"]:
                continue
            if field and field not in s["field_of_study"]:
                continue
            # TEMPORARY matching until the eligibility engine is built
            if has_profile and not searching:
                if s["degree_level"] and p.degree_level not in s["degree_level"]:
                    continue
                if s["field_of_study"] and p.field_of_study not in s["field_of_study"]:
                    continue
            results.append(s)

        # the colleges that offer the scholarships shown above
        colleges = {}
        for s in results:
            c = colleges.setdefault(s["provider"], {"name": s["provider"], "location": s["location"], "count": 0})
            c["count"] += 1

        mode = "search" if searching else ("matched" if has_profile else "all")
        items = [(s, None) for s in results]  # None = no eligibility result yet

        return render_template("dashboard.html", profile=p, items=items,
                               colleges=list(colleges.values()), mode=mode,
                               levels=LEVELS, fields=FIELDS)
    @app.route("/admin")
    @login_required
    def admin_home():
        if not current_user.is_admin:
            abort(403)
        return render_template("admin_home.html")

    @app.route("/profile", methods=["GET", "POST"])
    @login_required
    def profile():
        if current_user.is_admin:
            return redirect(url_for("admin_home"))
        p = current_user.profile or Profile(user_id=current_user.id)
        if request.method == "POST":
            f = request.form
            p.degree_level = f["degree_level"]
            p.field_of_study = f["field_of_study"]
            p.institution = f.get("institution", "").strip()
            p.course = f.get("course", "").strip()
            p.gpa = float(f["gpa"]) if f.get("gpa") else None
            p.location = f.get("location", "").strip()
            p.nationality = f.get("nationality", "Nepali").strip()
            p.income = int(f["income"]) if f.get("income") else None
            p.interests = f.get("interests", "").strip()
            db.session.add(p)
            db.session.commit()
            flash("Profile saved.", "success")
            return redirect(url_for("dashboard"))
        return render_template("profile.html", p=p, levels=LEVELS, fields=FIELDS)

    return app