#!/usr/bin/env python3
# app.py – PhishGuard back-end
# ─────────────────────────────────────────────────────────────
#
#  • Presentation : Flask + Jinja2 (HTML | CSS | JS | Bootstrap 5)
#  • Application  : Python 3.12 · Flask 3.x · REST APIs + ML logic
#  • Data layer   : SQLite (SQLAlchemy ORM)
#  • ML models    : utils.email_model / utils.url_model
#
#  NOTE: set SECRET_KEY and MAIL_* in a .env file (see README).

from __future__ import annotations
import os, time, datetime, logging, functools
from typing import Callable

import requests
from dotenv           import load_dotenv
from flask            import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify, abort
)
from flask_sqlalchemy import SQLAlchemy
from flask_login      import (
    LoginManager, login_user, login_required,
    logout_user, current_user, UserMixin
)
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous      import URLSafeTimedSerializer
from flask_mail        import Mail, Message
from sqlalchemy        import func

# ─────────────────── environment & logging ───────────────────
load_dotenv()
logging.basicConfig(
    level   = logging.INFO,
    format  = "%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt = "%H:%M:%S",
)

# ───────────────────────── Flask setup ───────────────────────
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE, exist_ok=True)
DB_FILE  = os.path.join(INSTANCE, "phishguard.db")

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config.update(
    SECRET_KEY                     = os.getenv("SECRET_KEY", "change-me"),
    SQLALCHEMY_DATABASE_URI        = f"sqlite:///{DB_FILE}",
    SQLALCHEMY_TRACK_MODIFICATIONS = False,

    MAIL_SERVER         = os.getenv("MAIL_SERVER",   "smtp.gmail.com"),
    MAIL_PORT           = int(os.getenv("MAIL_PORT", "587")),
    MAIL_USE_TLS        = os.getenv("MAIL_USE_TLS",  "True") == "True",
    MAIL_USERNAME       = os.getenv("MAIL_USERNAME", ""),
    MAIL_PASSWORD       = os.getenv("MAIL_PASSWORD", ""),
    MAIL_DEFAULT_SENDER = os.getenv(
        "MAIL_DEFAULT_SENDER",
        "PhishGuard Support <no-reply@example.com>"
    ),
)

db         = SQLAlchemy(app)
mail       = Mail(app)
serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

logging.info("⇢ Using database: %s", app.config["SQLALCHEMY_DATABASE_URI"])

# ──────────────────────────── models ─────────────────────────
class User(UserMixin, db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    email    = db.Column(db.String(150), unique=True, nullable=False)
    pw_hash  = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Prediction(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("user.id"))
    input_type = db.Column(db.String(10))   # "email" | "url"
    verdict    = db.Column(db.String(12))
    confidence = db.Column(db.Float)
    timestamp  = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class ContactMessage(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String(120))
    email     = db.Column(db.String(150))
    body      = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# ───────────────────── authentication helpers ────────────────
login_manager = LoginManager(app)
login_manager.login_view    = "login"
login_manager.login_message = None

@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return db.session.get(User, int(user_id))

def admin_required(fn: Callable):
    @functools.wraps(fn)
    def _wrap(*a, **kw):
        if not current_user.is_authenticated or not current_user.is_admin:
            return abort(403)
        return fn(*a, **kw)
    return _wrap

# ───────────────────── password-reset helpers ─────────────────
def send_reset_email(to_email: str) -> None:
    token = serializer.dumps(to_email, salt="password-reset")
    link  = url_for("reset_token", token=token, _external=True)

    msg = Message("PhishGuard Password Reset", recipients=[to_email])
    msg.body = (
        "Hello,\n\n"
        "To reset your password, click the link below (valid for 30 minutes):\n\n"
        f"{link}\n\n"
        "If you did not request a reset, please ignore this e-mail.\n\n"
        "— PhishGuard Team"
    )
    try:
        mail.send(msg)
        logging.info("✓ Reset link mailed to %s", to_email)
    except Exception as e:
        logging.warning("Mail send failed (%s) – printing link", e)
        print("\n==== PASSWORD RESET LINK ====\n", link)

def verify_reset_token(token: str, exp: int = 1800) -> str | None:
    try:
        return serializer.loads(token, salt="password-reset", max_age=exp)
    except Exception:
        return None

# ─────────────────────────── public views ────────────────────
@app.route("/")
def root():
    return redirect(url_for("home"))

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET","POST"])
def contact():
    if request.method == "POST":
        db.session.add(ContactMessage(
            name  = request.form["name"],
            email = request.form["email"],
            body  = request.form["message"],
        ))
        db.session.commit()
        flash("Thanks – we received your message!", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html")

@app.route("/reset_password", methods=["GET","POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email = request.form["email"].lower()
        if User.query.filter_by(email=email).first():
            send_reset_email(email)
        return render_template("confirm_sent.html")
    return render_template("reset_request.html")

@app.route("/reset_password/<token>", methods=["GET","POST"])
def reset_token(token: str):
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    email = verify_reset_token(token)
    if not email:
        flash("Reset link is invalid or expired.", "warning")
        return redirect(url_for("reset_request"))
    if request.method == "POST":
        user = User.query.filter_by(email=email).first()
        if user:
            user.pw_hash = generate_password_hash(request.form["password"])
            db.session.commit()
            flash("Password updated – you may now log in.", "success")
            return redirect(url_for("login"))
    return render_template("reset_token.html")

# ───────────── lazy ML loaders (singletons) ────────────────
_email_predict: Callable[[bytes], tuple[str, float]] | None = None
_url_predict:   Callable[[str], tuple[str, float]] | None = None

def get_email_predict():
    global _email_predict
    if _email_predict is None:
        logging.info("Loading e-mail model …")
        from utils.email_model import predict as _pred
        _email_predict = _pred
    return _email_predict

def get_url_predict():
    global _url_predict
    if _url_predict is None:
        logging.info("Loading URL model …")
        from utils.url_model import predict as _pred
        _url_predict = _pred
    return _url_predict

# ───────────────────────────── API routes ───────────────────
@app.post("/api/email")
@login_required
def api_email():
    f = request.files.get("file")
    if not f or not f.filename.lower().endswith(".eml"):
        return jsonify(error="No .eml file"), 400

    t0      = time.perf_counter()
    verdict, conf = get_email_predict()(f.read())
    ms      = int((time.perf_counter() - t0) * 1000)
    logging.info("E-mail scanned in %d ms → %s  %.3f", ms, verdict, conf)

    db.session.add(Prediction(
        user_id    = current_user.id,
        input_type = "email",
        verdict    = verdict,
        confidence = conf
    ))
    db.session.commit()

    return jsonify(verdict=verdict, confidence=conf), 200

@app.post("/api/url")
@login_required
def api_url():
    data    = request.get_json(silent=True) or {}
    raw_url = data.get("url", "").strip()
    if not raw_url:
        return jsonify(error="URL missing"), 400

    # 1) Normalize & ensure scheme
    if raw_url.lower().startswith(("http://", "https://")):
        url = raw_url
    else:
        url = "https://" + raw_url

    # 2) Reachability check with browser User-Agent
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        resp = requests.head(
            url,
            allow_redirects=True,
            timeout=3,
            headers=headers
        )
        # fallback to GET if Cloudflare blocks HEAD
        if resp.status_code == 403:
            resp = requests.get(
                url,
                allow_redirects=True,
                timeout=3,
                headers=headers,
                stream=True
            )
    except requests.RequestException as e:
        return jsonify(error="Network failure checking URL"), 502

    # 3) ── UPDATED: only fail on 5xx; allow 2xx–4xx (including 403) ─────────
    if resp.status_code >= 500:
        logging.info("Server‐side error checking URL → HTTP %d", resp.status_code)
        return (
            jsonify(
                error  = "Server error checking URL",
                status = resp.status_code
            ),
            resp.status_code
        )

    # 4) Only now do the ML scan
    t0      = time.perf_counter()
    verdict, conf = get_url_predict()(url)
    ms      = int((time.perf_counter() - t0) * 1000)
    logging.info("URL scanned in %d ms → %s  %.3f", ms, verdict, conf)

    # 5) Persist & return
    db.session.add(Prediction(
        user_id    = current_user.id,
        input_type = "url",
        verdict    = verdict,
        confidence = conf
    ))
    db.session.commit()

    return jsonify(verdict=verdict, confidence=conf), 200

@app.get("/api/history/pie")
@login_required
def history_pie():
    rows = db.session.query(Prediction.verdict, func.count().label("c")) \
                     .filter_by(user_id=current_user.id) \
                     .group_by(Prediction.verdict).all()
    return jsonify({v: int(c) for v, c in rows})

@app.get("/api/history/daily")
@login_required
def history_daily():
    rows = db.session.query(func.date(Prediction.timestamp).label("day"),
                             Prediction.verdict, func.count().label("c")) \
                     .filter_by(user_id=current_user.id) \
                     .group_by("day", Prediction.verdict).all()
    timeline: dict[str, dict[str, int]] = {}
    for day, v, c in rows:
        timeline.setdefault(str(day), {"Phishing":0,"Legitimate":0})[v] = int(c)
    return jsonify(timeline)

@app.get("/api/stats")
@login_required
def global_stats():
    total_scans    = Prediction.query.count()
    emails_scanned = Prediction.query.filter_by(input_type="email").count()
    malicious_urls = Prediction.query.filter_by(
        input_type="url", verdict="Phishing"
    ).count()

    detection_accuracy = (
        round((total_scans - malicious_urls) / total_scans * 100, 1)
        if total_scans > 0 else 0.0
    )

    return jsonify(
        emails_scanned     = emails_scanned,
        malicious_urls     = malicious_urls,
        detection_accuracy = detection_accuracy
    )

# ─────────────────────────── private UI ─────────────────────
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/email")
@login_required
def email_page():
    return render_template("scan_email.html")

@app.route("/url")
@login_required
def url_page():
    return render_template("scan_url.html")

@app.route("/messages")
@admin_required
def messages():
    msgs = ContactMessage.query.order_by(
        ContactMessage.timestamp.desc()
    ).all()
    return render_template("messages.html", msgs=msgs)

# ────────────────────────── auth UI ─────────────────────────
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        email = request.form["email"].lower()
        if User.query.filter_by(email=email).first():
            flash("Email already registered", "danger")
            return redirect(url_for("register"))
        user = User(email=email,
                    pw_hash=generate_password_hash(request.form["password"]))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("dashboard"))
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].lower()
        user  = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.pw_hash,
                                        request.form["password"]):
            login_user(user, remember=bool(request.form.get("remember")))
            return redirect(url_for("dashboard"))
        flash("Invalid credentials", "danger")
        return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# ───────────────────────────── main ─────────────────────────
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # create tables on first run
    app.run(debug=True)  # disable debug in production
