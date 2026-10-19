"""
NexaCorp Business Auth — FastAPI Backend (Local Development)
Database: SQLite (auto-created as nexacorp.db)
"""

import os
import sqlite3
import hashlib
import hmac
import secrets
import time
from datetime import datetime, timezone
from contextlib import contextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
DB_PATH    = os.getenv("DB_PATH", "nexacorp.db")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="NexaCorp Auth API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Database ──────────────────────────────────────────────────────────────────
@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name   TEXT    NOT NULL,
                email       TEXT    NOT NULL UNIQUE,
                company     TEXT    DEFAULT '',
                password_hash TEXT NOT NULL,
                created_at  TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS login_logs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email  TEXT    NOT NULL,
                logged_at   TEXT    NOT NULL
            );
        """)
    print("✅ Database initialized:", DB_PATH)

init_db()

# ── Password utils ────────────────────────────────────────────────────────────
def hash_password(pw: str) -> str:
    salt = secrets.token_hex(16)
    h    = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 260_000)
    return f"{salt}:{h.hex()}"

def verify_password(pw: str, stored: str) -> bool:
    try:
        salt, h = stored.split(":", 1)
        check = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 260_000)
        return hmac.compare_digest(check.hex(), h)
    except Exception:
        return False

def make_token(email: str) -> str:
    ts      = int(time.time())
    payload = f"{email}:{ts}"
    sig     = hmac.new(SECRET_KEY.encode(), payload.encode(), "sha256").hexdigest()
    return f"{payload}:{sig}"

# ── Schemas ────────────────────────────────────────────────────────────────────
class SignupRequest(BaseModel):
    full_name: str
    email:     str
    company:   str = ""
    password:  str

class LoginRequest(BaseModel):
    email:    str
    password: str

# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.post("/signup")
def signup(req: SignupRequest):
    if len(req.full_name.strip()) < 2:
        raise HTTPException(400, "Full name must be at least 2 characters.")
    if "@" not in req.email or "." not in req.email:
        raise HTTPException(400, "Invalid email address.")
    if len(req.password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters.")

    now = datetime.now(timezone.utc).isoformat()

    with get_db() as conn:
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (req.email.lower(),)).fetchone()
        if existing:
            raise HTTPException(409, "An account with this email already exists.")

        conn.execute(
            "INSERT INTO users (full_name, email, company, password_hash, created_at) VALUES (?,?,?,?,?)",
            (req.full_name.strip(), req.email.lower(), req.company.strip(), hash_password(req.password), now),
        )

    return {"message": "Account created successfully.", "email": req.email.lower()}


@app.post("/login")
def login(req: LoginRequest):
    with get_db() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (req.email.lower(),)
        ).fetchone()

        if not user or not verify_password(req.password, user["password_hash"]):
            raise HTTPException(401, "Invalid email or password.")

        # Log the login event
        conn.execute(
            "INSERT INTO login_logs (user_email, logged_at) VALUES (?,?)",
            (req.email.lower(), datetime.now(timezone.utc).isoformat()),
        )

    token = make_token(req.email.lower())
    return {
        "token": token,
        "user": {
            "full_name": user["full_name"],
            "email":     user["email"],
            "company":   user["company"],
        },
    }


@app.get("/stats")
def stats():
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

    with get_db() as conn:
        total_users      = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_companies  = conn.execute(
            "SELECT COUNT(DISTINCT company) FROM users WHERE company != ''"
        ).fetchone()[0]
        logins_today     = conn.execute(
            "SELECT COUNT(*) FROM login_logs WHERE logged_at >= ?", (today_start,)
        ).fetchone()[0]
        total_logins     = conn.execute("SELECT COUNT(*) FROM login_logs").fetchone()[0]

        # Recent 10 signups
        rows = conn.execute(
            "SELECT full_name, company, created_at FROM users ORDER BY id DESC LIMIT 10"
        ).fetchall()
        recent_users = [dict(r) for r in rows]

        # 7-day trend
        trend_7d = []
        from datetime import timedelta
        for i in range(6, -1, -1):
            day  = (datetime.now(timezone.utc) - timedelta(days=i)).date()
            day_str = str(day)
            count = conn.execute(
                "SELECT COUNT(*) FROM users WHERE created_at LIKE ?", (f"{day_str}%",)
            ).fetchone()[0]
            label = day.strftime("%a")
            trend_7d.append({"day": label, "count": count})

    return {
        "total_users":     total_users,
        "total_companies": total_companies,
        "logins_today":    logins_today,
        "total_logins":    total_logins,
        "recent_users":    recent_users,
        "trend_7d":        trend_7d,
    }


# ── Serve frontend ────────────────────────────────────────────────────────────
frontend = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(frontend):
    app.mount("/static", StaticFiles(directory=frontend), name="static")

    @app.get("/")
    def index():
        return FileResponse(os.path.join(frontend, "login.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
