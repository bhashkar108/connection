/**
 * NexaCorp — Sign Up Page Script
 * Handles form validation, password strength, API signup call, and live counter.
 */

const API = (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
  ? "http://localhost:8000"
  : "";

/* ── DOM refs ──────────────────────────────────────────────────────────────── */
const form       = document.getElementById("signupForm");
const nameEl     = document.getElementById("fullName");
const companyEl  = document.getElementById("company");
const emailEl    = document.getElementById("email");
const pwEl       = document.getElementById("password");
const confirmEl  = document.getElementById("confirmPw");
const termsEl    = document.getElementById("agreeTerms");
const nameErr    = document.getElementById("nameErr");
const emailErr   = document.getElementById("emailErr");
const pwErr      = document.getElementById("pwErr");
const confirmErr = document.getElementById("confirmErr");
const termsErr   = document.getElementById("termsErr");
const alertBox   = document.getElementById("alertBox");
const alertMsg   = document.getElementById("alertMsg");
const submitBtn  = document.getElementById("submitBtn");
const btnText    = document.getElementById("btnText");
const btnLoader  = document.getElementById("btnLoader");
const togglePw   = document.getElementById("togglePw");
const eyeIcon    = document.getElementById("eyeIcon");
const pwBar      = document.getElementById("pwBar");
const pwLabel    = document.getElementById("pwLabel");
const joinText   = document.getElementById("joinCounterText");

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
  btnText.textContent = on ? "Creating Account…" : "Create Account";
  btnLoader.classList.toggle("hidden", !on);
}

function isValidEmail(v) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v); }

/* ── Toggle password ──────────────────────────────────────────────────────── */
togglePw.addEventListener("click", () => {
  const isHidden = pwEl.type === "password";
  pwEl.type = isHidden ? "text" : "password";
  eyeIcon.textContent = isHidden ? "🙈" : "👁";
});

/* ── Password strength meter ──────────────────────────────────────────────── */
const STRENGTH = [
  { label: "",         color: "",          width: "0%" },
  { label: "Weak",     color: "#EF4444",   width: "25%" },
  { label: "Fair",     color: "#F59E0B",   width: "50%" },
  { label: "Good",     color: "#3B82F6",   width: "75%" },
  { label: "Strong",   color: "#10B981",   width: "100%" },
];

function getStrength(pw) {
  let score = 0;
  if (pw.length >= 8)  score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  return score;
}

pwEl.addEventListener("input", () => {
  const score = pwEl.value ? getStrength(pwEl.value) : 0;
  const s = STRENGTH[score];
  pwBar.style.width       = s.width;
  pwBar.style.background  = s.color;
  pwLabel.textContent     = s.label;
  pwLabel.style.color     = s.color;
});

/* ── Inline validation ────────────────────────────────────────────────────── */
nameEl.addEventListener("blur", () => {
  const ok = nameEl.value.trim().length >= 2;
  nameEl.classList.toggle("input--error", !ok);
  nameErr.classList.toggle("hidden", ok);
});

emailEl.addEventListener("blur", () => {
  const ok = isValidEmail(emailEl.value.trim());
  emailEl.classList.toggle("input--error", !ok && emailEl.value.trim() !== "");
  emailErr.classList.toggle("hidden", ok || emailEl.value.trim() === "");
});

pwEl.addEventListener("blur", () => {
  const ok = pwEl.value.length >= 8;
  pwEl.classList.toggle("input--error", !ok);
  pwErr.classList.toggle("hidden", ok || !pwEl.value);
});

confirmEl.addEventListener("blur", () => {
  const ok = confirmEl.value === pwEl.value && confirmEl.value.length > 0;
  confirmEl.classList.toggle("input--error", !ok && confirmEl.value.length > 0);
  confirmErr.classList.toggle("hidden", ok || confirmEl.value.length === 0);
});

/* ── Form submit ───────────────────────────────────────────────────────────── */
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  hideAlert();

  const fullName  = nameEl.value.trim();
  const company   = companyEl.value.trim();
  const email     = emailEl.value.trim();
  const password  = pwEl.value;
  const confirmPw = confirmEl.value;

  let valid = true;

  if (fullName.length < 2) {
    nameEl.classList.add("input--error");
    nameErr.classList.remove("hidden");
    valid = false;
  }
  if (!isValidEmail(email)) {
    emailEl.classList.add("input--error");
    emailErr.classList.remove("hidden");
    valid = false;
  }
  if (password.length < 8) {
    pwEl.classList.add("input--error");
    pwErr.classList.remove("hidden");
    valid = false;
  }
  if (password !== confirmPw) {
    confirmEl.classList.add("input--error");
    confirmErr.classList.remove("hidden");
    valid = false;
  }
  if (!termsEl.checked) {
    termsErr.classList.remove("hidden");
    valid = false;
  } else {
    termsErr.classList.add("hidden");
  }

  if (!valid) return;

  setLoading(true);

  try {
    const res = await fetch(`${API}/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ full_name: fullName, company, email, password }),
      signal: AbortSignal.timeout(15_000),
    });

    const data = await res.json();

    if (!res.ok) {
      showAlert(data.detail || "Registration failed. Please try again.", "error");
      return;
    }

    showAlert("🎉 Account created successfully! Redirecting to sign in…", "success");
    setTimeout(() => { window.location.href = "login.html"; }, 1800);

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

/* ── Live join counter on brand panel ─────────────────────────────────────── */
async function loadJoinCounter() {
  try {
    const res  = await fetch(`${API}/stats`, { signal: AbortSignal.timeout(5000) });
    const data = await res.json();
    const total = data.total_users ?? 0;
    const fmt   = total >= 1000 ? (total / 1000).toFixed(1) + "k" : String(total);
    joinText.textContent = `🚀 ${fmt} businesses have already signed up!`;
  } catch {
    joinText.textContent = "🚀 Join thousands of growing businesses!";
  }
}

loadJoinCounter();
