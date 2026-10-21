# 🏢 NexaCorp — Business Auth Portal

<div align="center">

![NexaCorp Banner](https://img.shields.io/badge/NexaCorp-Business%20Portal-2563EB?style=for-the-badge&logo=google-chrome&logoColor=white)

[![HTML](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![CSS](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Netlify](https://img.shields.io/badge/Netlify-00C7B7?style=flat-square&logo=netlify&logoColor=white)](https://netlify.com)

**A premium, modern business authentication system with live statistics dashboard.**

[🔐 Login Page](#-pages) · [📝 Sign Up Page](#-pages) · [📊 Stats Dashboard](#-pages) · [🚀 Deploy](#-deploy-to-netlify)

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 **Secure Login** | Email + password login with session token |
| 📝 **User Registration** | Full name, company, email, password signup |
| 💪 **Password Strength Meter** | Real-time password strength indicator |
| 📊 **Live Stats Dashboard** | Shows total users, logins today, companies & trend chart |
| 🕒 **Recent Signups Table** | Live table of last 10 registered users |
| 📈 **7-Day Trend Chart** | Visual bar chart of signups over last 7 days |
| 🔄 **Auto Refresh** | Stats page refreshes every 30 seconds automatically |
| 📱 **Fully Responsive** | Works perfectly on mobile, tablet and desktop |
| 🔒 **Secure Passwords** | PBKDF2 hashing — passwords never stored in plain text |
| ⚡ **Serverless Ready** | Netlify Functions support for cloud deployment |

---

## 📄 Pages

### 🔐 Login Page (`login.html`)
- Premium split-screen design
- Left side: Brand panel with **live user counter**
- Right side: Clean login form
- Remember me option
- Forgot password link
- Instant validation feedback

### 📝 Sign Up Page (`signup.html`)
- Full registration form (Name, Company, Email, Password)
- **Real-time password strength meter** (Weak → Fair → Good → Strong)
- Terms & Conditions checkbox
- Live counter: *"X businesses have already signed up!"*
- Smooth error validation

### 📊 Stats Dashboard (`stats.html`)
- **4 animated stat cards:**
  - 👥 Total Registered Users
  - 🔐 Logins Today
  - 🏢 Companies Onboarded
  - ⚡ Total Logins (All Time)
- **Recent Signups Table** — last 10 registrations
- **7-Day Bar Chart** — signup trend visualization
- 🟢 Live indicator — auto-refreshes every 30 seconds

---

## 📁 File Structure

```
📦 Repository
 ┣ 📄 login.html                ← Login page
 ┣ 📄 signup.html               ← Sign up page
 ┣ 📄 stats.html                ← Live stats dashboard
 ┣ 📄 style.css                 ← All styles (premium design)
 ┣ 📄 login.js                  ← Login page script
 ┣ 📄 signup.js                 ← Signup page script
 ┣ 📄 stats.js                  ← Stats dashboard script
 ┣ 📄 main.py                   ← FastAPI backend (local dev)
 ┣ 📄 login.py                  ← Netlify serverless function
 ┣ 📄 signup.py                 ← Netlify serverless function
 ┣ 📄 stats.py                  ← Netlify serverless function
 ┣ 📄 backend_requirements.txt  ← Python packages (local)
 ┣ 📄 functions_requirements.txt← Python packages (Netlify)
 ┣ 📄 netlify.toml              ← Netlify configuration
 ┗ 📄 .env.example              ← Environment variable template
```

---

## 🖥️ Run Locally

### Step 1 — Install Python packages

```bash
pip install -r backend_requirements.txt
```

### Step 2 — Setup environment

```bash
# Copy the template
copy .env.example .env

# Open .env and set your secret key
# SECRET_KEY=your_long_random_secret_key_here
```

### Step 3 — Start the server

```bash
python main.py
```

### Step 4 — Open in browser

```
http://localhost:8000/login.html
```

> ✅ SQLite database (`nexacorp.db`) will be created automatically on first run.

---

## 🚀 Deploy to Netlify

### Step 1 — Setup Supabase (Free Database)

1. Go to **https://supabase.com** → Create free account
2. Create a new project
3. Go to **SQL Editor** and run:

```sql
CREATE TABLE users (
  id           UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  full_name    TEXT NOT NULL,
  email        TEXT UNIQUE NOT NULL,
  company      TEXT DEFAULT '',
  password_hash TEXT NOT NULL,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE login_logs (
  id         UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_email TEXT NOT NULL,
  logged_at  TIMESTAMPTZ DEFAULT NOW()
);
```

4. Go to **Settings → API** and copy:
   - `Project URL` → this is your `SUPABASE_URL`
   - `service_role` key → this is your `SUPABASE_KEY`

### Step 2 — Deploy to Netlify

1. Go to **https://app.netlify.com** → **Add new site** → **Import from Git**
2. Connect your GitHub and select this repository
3. Build settings (auto-detected from `netlify.toml`):
   - Publish directory: `.` *(root)*
   - Functions directory: `netlify/functions`
4. Click **Deploy site**

### Step 3 — Add Environment Variables

In Netlify → **Site configuration** → **Environment variables**, add:

| Key | Value |
|---|---|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Your Supabase service_role key |
| `SECRET_KEY` | Any long random string |

5. Go to **Deploys** → **Trigger deploy** → **Deploy site**

---

## 🔐 Security Features

- ✅ Passwords hashed with **PBKDF2-SHA256** (260,000 iterations)
- ✅ API keys stored in **environment variables only** — never in code
- ✅ **XSS protection** on all user-generated content
- ✅ **HTTPS enforced** on Netlify deployment
- ✅ Security headers configured in `netlify.toml`

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Backend (Local)** | Python, FastAPI, SQLite |
| **Backend (Cloud)** | Netlify Functions (Python Serverless) |
| **Database (Cloud)** | Supabase (PostgreSQL) |
| **Deployment** | Netlify (CDN + Serverless) |
| **Auth** | Custom PBKDF2 password hashing + HMAC tokens |

---

## 🧪 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/signup` | Register a new user |
| `POST` | `/login` | Login and get token |
| `GET` | `/stats` | Get live platform statistics |

### Example — Signup Request
```json
{
  "full_name": "John Smith",
  "email": "john@company.com",
  "company": "Acme Corp",
  "password": "SecurePass123!"
}
```

### Example — Stats Response
```json
{
  "total_users": 142,
  "logins_today": 38,
  "total_companies": 61,
  "total_logins": 890,
  "recent_users": [...],
  "trend_7d": [...]
}
```

---

## 📱 Responsive Design

| Device | Layout |
|---|---|
| 🖥️ Desktop (>900px) | Split-screen — Brand left, Form right |
| 📱 Tablet (580–900px) | Single column — Form only |
| 📱 Mobile (<580px) | Compact single column |

---

## 🚨 Troubleshooting

| Problem | Solution |
|---|---|
| "Cannot connect to server" | Run `python main.py` and check port 8000 |
| "Database not configured" | Add `SUPABASE_URL` & `SUPABASE_KEY` in Netlify env vars |
| Stats show "—" | Backend is offline or Supabase not connected |
| Signup fails with 409 | Email already registered — use a different email |
| Netlify function timeout | Check Netlify Function logs under **Functions** tab |

---

## 👨‍💻 Author

**bhashkar108** · [GitHub](https://github.com/bhashkar108/connection)

---

<div align="center">

Made with ❤️ · © 2026 NexaCorp

⭐ **Star this repo if you found it helpful!**

</div>
