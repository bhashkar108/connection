"""
NexaCorp — Netlify Serverless Function: POST /login
Uses Supabase (PostgreSQL) as the cloud database.
"""

import json, os, hashlib, hmac, secrets, time
from datetime import datetime, timezone

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
SECRET_KEY   = os.environ.get("SECRET_KEY", "changeme")


def cors_headers():
    return {
        "Access-Control-Allow-Origin":  "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Content-Type": "application/json",
    }

def resp(status, body):
    return {"statusCode": status, "headers": cors_headers(), "body": json.dumps(body)}

def verify_password(pw, stored):
    try:
        salt, h = stored.split(":", 1)
        check = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 260_000)
        return hmac.compare_digest(check.hex(), h)
    except Exception:
        return False

def make_token(email):
    ts      = int(time.time())
    payload = f"{email}:{ts}"
    sig     = hmac.new(SECRET_KEY.encode(), payload.encode(), "sha256").hexdigest()
    return f"{payload}:{sig}"

def supabase_get(table, params=""):
    import urllib.request
    url = f"{SUPABASE_URL}/rest/v1/{table}{params}"
    req = urllib.request.Request(url, headers={
        "apikey":        SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type":  "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())
    except Exception as ex:
        return 500, {"message": str(ex)}

def supabase_post(table, payload):
    import urllib.request
    url  = f"{SUPABASE_URL}/rest/v1/{table}"
    data = json.dumps(payload).encode()
    req  = urllib.request.Request(url, data=data, headers={
        "apikey":        SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type":  "application/json",
        "Prefer":        "return=minimal",
    }, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, {}
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception:
        return 500, {}


def handler(event, context):
    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": cors_headers(), "body": ""}

    if event.get("httpMethod") != "POST":
        return resp(405, {"detail": "Method not allowed."})

    if not SUPABASE_URL or not SUPABASE_KEY:
        return resp(503, {"detail": "Database not configured. Set SUPABASE_URL and SUPABASE_KEY in Netlify environment variables."})

    try:
        body     = json.loads(event.get("body") or "{}")
        email    = (body.get("email") or "").strip().lower()
        password = body.get("password") or ""

        if not email or not password:
            return resp(400, {"detail": "Email and password are required."})

        # Fetch user
        status, users = supabase_get("users", f"?email=eq.{email}&select=*")
        if status != 200 or len(users) == 0:
            return resp(401, {"detail": "Invalid email or password."})

        user = users[0]

        if not verify_password(password, user.get("password_hash", "")):
            return resp(401, {"detail": "Invalid email or password."})

        # Log login event
        supabase_post("login_logs", {
            "user_email": email,
            "logged_at":  datetime.now(timezone.utc).isoformat(),
        })

        return resp(200, {
            "token": make_token(email),
            "user":  {
                "full_name": user.get("full_name"),
                "email":     user.get("email"),
                "company":   user.get("company", ""),
            },
        })

    except Exception as e:
        return resp(500, {"detail": str(e)})
