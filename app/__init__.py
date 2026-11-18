from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from .eligibility import check
from .recommender import order_by_interest


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

    from .models import User, Profile, Scholarship

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
    
    @app.route("/profile", methods=["GET", "POST"])
    @login_required
    def profile():
        if current_user.is_admin:
            return redirect(url_for("admin_home"))
        p = current_user.profile
        if request.method == "POST":
            if p is None:
                p = Profile(user_id=current_user.id)
                db.session.add(p)
            p.degree_level = request.form.get("degree_level", "")
            p.field_of_study = request.form.get("field_of_study", "")
            p.institution = request.form.get("institution", "").strip()
            p.course = request.form.get("course", "").strip()
            gpa = request.form.get("gpa", "").strip()
            p.gpa = float(gpa) if gpa else None
            p.location = request.form.get("location", "").strip()
            p.nationality = request.form.get("nationality", "").strip() or "Nepali"
            income = request.form.get("income", "").strip()
            p.income = int(income) if income else None
            p.interests = request.form.get("interests", "").strip()
            db.session.commit()
            flash("Profile saved.", "success")
            return redirect(url_for("dashboard"))
        return render_template("profile.html", p=p or Profile(), levels=LEVELS, fields=FIELDS)
    @app.route("/admin")
    @login_required
    def admin_home():
        if not current_user.is_admin:
            abort(403)
        return render_template("admin_home.html")
    
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
        show = request.args.get("show", "matches")
        searching = bool(q or level or field)

        # only verified scholarships are visible to students
        rows = Scholarship.query.filter_by(status="verified").order_by(Scholarship.id).all()

        # 1. search text and filters (+ the eligibility check when there is a profile)
        found = []
        for s in rows:
            degrees = s.degree_level or ""
            fields_ = s.field_of_study or ""
            if q and q not in f"{s.title} {s.description or ''}".lower():
                continue
            if level and level not in degrees:
                continue
            if field and field not in fields_:
                continue
            r = check(p, s) if has_profile else None
            found.append((s, r))

        # 2. with a profile: count each result type, then keep the ones chosen in the tabs
        tabs = []
        results = found
        if has_profile:
            count = {"eligible": 0, "close": 0, "not": 0}
            for s, r in found:
                count[r["status"]] += 1

            wanted = {"matches": ("eligible", "close"), "eligible": ("eligible",),
                      "close": ("close",), "not": ("not",),
                      "all": ("eligible", "close", "not")}.get(show, ("eligible", "close"))
            results = [(s, r) for s, r in found if r["status"] in wanted]

            order = {"eligible": 0, "close": 1, "not": 2}      # best first
            results.sort(key=lambda item: order[item[1]["status"]])
            # Interest ordering applies only to the scholarships the student is
            # eligible for. Close matches and not-eligible ones keep their order,
            # so interest can never change which group a scholarship is in.
            eligible_part = [item for item in results if item[1]["status"] == "eligible"]
            other_part = [item for item in results if item[1]["status"] != "eligible"]
            results = order_by_interest(p, eligible_part) + other_part

            base = request.args.to_dict()
            for key, label in [("matches", f"Best matches ({count['eligible'] + count['close']})"),
                               ("eligible", f"Eligible ({count['eligible']})"),
                               ("close", f"Close match ({count['close']})"),
                               ("not", f"Not eligible ({count['not']})"),
                               ("all", "Everything")]:
                tabs.append({"label": label, "active": key == show,
                             "url": url_for("dashboard", **{**base, "show": key})})

        # 3. the colleges that offer the scholarships shown
        colleges = {}
        for s, r in results:
            name = s.provider or "Other providers"
            c = colleges.setdefault(name, {"name": name, "location": s.location or "", "count": 0})
            c["count"] += 1

        mode = "search" if searching else ("matched" if has_profile else "all")

        return render_template("dashboard.html", profile=p, items=results,
                               colleges=list(colleges.values()), mode=mode, tabs=tabs,
                               levels=LEVELS, fields=FIELDS)
    return app
