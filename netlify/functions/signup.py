"""
NexaCorp — Netlify Serverless Function: POST /signup
Uses Supabase (PostgreSQL) as the cloud database.
Set SUPABASE_URL and SUPABASE_KEY in Netlify → Environment Variables.
"""

import json, os, hashlib, hmac, secrets
from datetime import datetime, timezone

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")   # service_role key


def cors_headers():
    return {
        "Access-Control-Allow-Origin":  "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Content-Type": "application/json",
    }

def resp(status, body):
    return {"statusCode": status, "headers": cors_headers(), "body": json.dumps(body)}

def hash_password(pw):
    salt = secrets.token_hex(16)
    h    = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 260_000)
    return f"{salt}:{h.hex()}"

def supabase_request(method, table, payload=None, params=""):
    import urllib.request
    url = f"{SUPABASE_URL}/rest/v1/{table}{params}"
    headers_sb = {
        "apikey":        SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type":  "application/json",
        "Prefer":        "return=representation",
    }
    data = json.dumps(payload).encode() if payload else None
    req  = urllib.request.Request(url, data=data, headers=headers_sb, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())
    except Exception as ex:
        return 500, {"message": str(ex)}


def handler(event, context):
    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": cors_headers(), "body": ""}

    if event.get("httpMethod") != "POST":
        return resp(405, {"detail": "Method not allowed."})

    if not SUPABASE_URL or not SUPABASE_KEY:
        return resp(503, {"detail": "Database not configured. Set SUPABASE_URL and SUPABASE_KEY in Netlify environment variables."})

    try:
        body     = json.loads(event.get("body") or "{}")
        name     = (body.get("full_name") or "").strip()
        email    = (body.get("email") or "").strip().lower()
        company  = (body.get("company") or "").strip()
        password = body.get("password") or ""

        if len(name) < 2:
            return resp(400, {"detail": "Full name must be at least 2 characters."})
        if "@" not in email or "." not in email:
            return resp(400, {"detail": "Invalid email address."})
        if len(password) < 8:
            return resp(400, {"detail": "Password must be at least 8 characters."})

        # Check for duplicate email
        status, existing = supabase_request("GET", "users", params=f"?email=eq.{email}&select=id")
        if status == 200 and len(existing) > 0:
            return resp(409, {"detail": "An account with this email already exists."})

        now = datetime.now(timezone.utc).isoformat()
        status, result = supabase_request("POST", "users", {
            "full_name":     name,
            "email":         email,
            "company":       company,
            "password_hash": hash_password(password),
            "created_at":    now,
        })

        if status not in (200, 201):
            return resp(500, {"detail": "Failed to create account. Please try again."})

        return resp(201, {"message": "Account created successfully."})

    except Exception as e:
        return resp(500, {"detail": str(e)})
