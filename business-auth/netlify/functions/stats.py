"""
NexaCorp — Netlify Serverless Function: GET /stats
Returns live user/login counts, recent signups, and 7-day trend.
"""

import json, os
from datetime import datetime, timezone, timedelta
import urllib.request

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")


def cors_headers():
    return {
        "Access-Control-Allow-Origin":  "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Content-Type": "application/json",
    }

def resp(status, body):
    return {"statusCode": status, "headers": cors_headers(), "body": json.dumps(body)}

def sb_get(table, params=""):
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
        return e.code, []
    except Exception:
        return 500, []


def handler(event, context):
    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": cors_headers(), "body": ""}

    if not SUPABASE_URL or not SUPABASE_KEY:
        return resp(503, {"detail": "Database not configured."})

    try:
        now   = datetime.now(timezone.utc)
        today = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

        # Total users
        _, all_users    = sb_get("users",      "?select=id,full_name,company,created_at")
        # Total logins
        _, all_logins   = sb_get("login_logs", "?select=id")
        # Logins today
        _, today_logins = sb_get("login_logs", f"?logged_at=gte.{today}&select=id")

        total_users     = len(all_users)    if isinstance(all_users,  list) else 0
        total_logins    = len(all_logins)   if isinstance(all_logins,  list) else 0
        logins_today    = len(today_logins) if isinstance(today_logins, list) else 0

        # Companies
        companies = set()
        for u in (all_users if isinstance(all_users, list) else []):
            c = (u.get("company") or "").strip()
            if c:
                companies.add(c.lower())
        total_companies = len(companies)

        # Recent 10 signups
        _, recent_rows = sb_get(
            "users",
            "?select=full_name,company,created_at&order=created_at.desc&limit=10"
        )
        recent_users = recent_rows if isinstance(recent_rows, list) else []

        # 7-day signup trend
        trend_7d = []
        for i in range(6, -1, -1):
            day       = (now - timedelta(days=i)).date()
            day_start = f"{day}T00:00:00+00:00"
            day_end   = f"{day}T23:59:59+00:00"
            _, day_users = sb_get(
                "users",
                f"?created_at=gte.{day_start}&created_at=lte.{day_end}&select=id"
            )
            count = len(day_users) if isinstance(day_users, list) else 0
            trend_7d.append({
                "day":   day.strftime("%a"),
                "count": count,
            })

        return resp(200, {
            "total_users":     total_users,
            "total_companies": total_companies,
            "logins_today":    logins_today,
            "total_logins":    total_logins,
            "recent_users":    recent_users,
            "trend_7d":        trend_7d,
        })

    except Exception as e:
        return resp(500, {"detail": str(e)})
