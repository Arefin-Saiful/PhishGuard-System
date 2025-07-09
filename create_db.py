"""
create_db.py – run once to initialise instance/phishguard.db

Usage:
    (venv) $ python create_db.py
"""
from __future__ import annotations
import os
from app import app, db                         # import your Flask app

# ── resolve the actual SQLite file path ─────────────────────────
uri      = app.config["SQLALCHEMY_DATABASE_URI"]        # sqlite:///...
db_path  = uri.replace("sqlite:///", "", 1)

print("Using database URI :", uri)
print("Resolved file path :", db_path)
print("Parent folder exists?:", os.path.exists(os.path.dirname(db_path)))

# ── create tables inside an application-context ─────────────────
with app.app_context():
    db.create_all()
    print("✓ tables created")

print("DB file exists? ->", os.path.exists(db_path))
