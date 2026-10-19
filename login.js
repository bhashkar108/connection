/**
 * NexaCorp — Login Page Script
 * Handles form validation, API call, and live stats on brand panel.
 */

const API = (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
  ? "http://localhost:8000"
  : "";

/* ── DOM refs ──────────────────────────────────────────────────────────────── */
const form      = document.getElementById("loginForm");
const emailEl   = document.getElementById("email");
const pwEl      = document.getElementById("password");
const emailErr  = document.getElementById("emailErr");
const pwErr     = document.getElementById("pwErr");
const alertBox  = document.getElementById("alertBox");
const alertMsg  = document.getElementById("alertMsg");
const submitBtn = document.getElementById("submitBtn");
const btnText   = document.getElementById("btnText");
const btnLoader = document.getElementById("btnLoader");
const togglePw  = document.getElementById("togglePw");
const eyeIcon   = document.getElementById("eyeIcon");

/* ── Helpers ──────────────────────────────────────────────────────────────── */
function showAlert(msg, type = "error") {
  alertBox.className = `alert alert--${type}`;
  alertBox.querySelector(".alert__icon").textContent = type === "error" ? "⚠️" : "✅";
  alertMsg.textContent = msg;
  alertBox.classList.remove("hidden");
  alertBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function hideAlert() { alertBox.classList.add("hidden"); }

function setLoading(on) {
  submitBtn.disabled = on;
  btnText.textContent = on ? "Signing in…" : "Sign In";
  btnLoader.classList.toggle("hidden", !on);
}

function isValidEmail(v) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v); }

/* ── Toggle password visibility ───────────────────────────────────────────── */
togglePw.addEventListener("click", () => {
  const isHidden = pwEl.type === "password";
  pwEl.type = isHidden ? "text" : "password";
  eyeIcon.textContent = isHidden ? "🙈" : "👁";
});

/* ── Inline validation ────────────────────────────────────────────────────── */
emailEl.addEventListener("blur", () => {
  const ok = isValidEmail(emailEl.value.trim());
  emailEl.classList.toggle("input--error", !ok && emailEl.value.trim() !== "");
  emailErr.classList.toggle("hidden", ok || emailEl.value.trim() === "");
});

pwEl.addEventListener("blur", () => {
  const ok = pwEl.value.length > 0;
  pwEl.classList.toggle("input--error", !ok);
  pwErr.classList.toggle("hidden", ok);
});

/* ── Form submit ───────────────────────────────────────────────────────────── */
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  hideAlert();

  const email    = emailEl.value.trim();
  const password = pwEl.value;

  // Client-side validation
  let valid = true;
  if (!isValidEmail(email)) {
    emailEl.classList.add("input--error");
    emailErr.classList.remove("hidden");
    valid = false;
  }
  if (!password) {
    pwEl.classList.add("input--error");
    pwErr.classList.remove("hidden");
    valid = false;
  }
  if (!valid) return;

  setLoading(true);

  try {
    const res = await fetch(`${API}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
      signal: AbortSignal.timeout(15_000),
    });

    const data = await res.json();

    if (!res.ok) {
      showAlert(data.detail || "Invalid email or password. Please try again.", "error");
      return;
    }

    // Success — store token and redirect
    if (data.token) localStorage.setItem("nexacorp_token", data.token);
    if (data.user) localStorage.setItem("nexacorp_user", JSON.stringify(data.user));

    showAlert(`Welcome back, ${data.user?.full_name || "User"}! Redirecting…`, "success");
    setTimeout(() => { window.location.href = "stats.html"; }, 1200);

  } catch (err) {
    if (err.name === "TimeoutError" || err.message.includes("fetch")) {
      showAlert("Cannot connect to server. Make sure the backend is running.", "error");
    } else {
      showAlert("Something went wrong. Please try again.", "error");
    }
  } finally {
    setLoading(false);
  }
});

/* ── Load live stats for brand panel ─────────────────────────────────────── */
async function loadBrandStats() {
  try {
    const res  = await fetch(`${API}/stats`, { signal: AbortSignal.timeout(5000) });
    const data = await res.json();

    const fmt = n => n >= 1000 ? (n / 1000).toFixed(1) + "k" : String(n);

    document.getElementById("statUsers").textContent     = fmt(data.total_users    ?? 0);
    document.getElementById("statLogins").textContent    = fmt(data.logins_today   ?? 0);
    document.getElementById("statCompanies").textContent = fmt(data.total_companies ?? 0);
  } catch {
    // Silently fail — stats are decorative on the login page
    ["statUsers", "statLogins", "statCompanies"].forEach(id => {
      document.getElementById(id).textContent = "—";
    });
  }
}

loadBrandStats();
