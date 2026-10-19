/**
 * NexaCorp — Statistics Page Script
 * Loads live stats, animates counters, renders table and bar chart.
 */

const API = (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
  ? "http://localhost:8000"
  : "";

/* ── Animated counter ─────────────────────────────────────────────────────── */
function animateCounter(el, target, duration = 1200) {
  const start = performance.now();
  const from  = 0;

  function step(now) {
    const elapsed  = now - start;
    const progress = Math.min(elapsed / duration, 1);
    // Ease out cubic
    const eased    = 1 - Math.pow(1 - progress, 3);
    const value    = Math.round(from + eased * (target - from));
    el.textContent = value.toLocaleString("en-IN");
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

/* ── Render recent signups table ──────────────────────────────────────────── */
function renderTable(users) {
  const tbody = document.getElementById("recentBody");

  if (!users || users.length === 0) {
    tbody.innerHTML = `<tr><td colspan="4" class="table-loading">No signups yet. Be the first!</td></tr>`;
    return;
  }

  tbody.innerHTML = users.map((u, i) => `
    <tr class="fade-in" style="animation-delay:${i * 50}ms">
      <td><strong>${i + 1}</strong></td>
      <td>${escHtml(u.full_name)}</td>
      <td>${escHtml(u.company || "—")}</td>
      <td>${formatDate(u.created_at)}</td>
    </tr>
  `).join("");
}

/* ── Render bar chart ─────────────────────────────────────────────────────── */
function renderBarChart(trend) {
  const container = document.getElementById("barChart");

  if (!trend || trend.length === 0) {
    container.innerHTML = `<div class="bar-chart__loading">No data available yet.</div>`;
    return;
  }

  const max = Math.max(...trend.map(d => d.count), 1);

  container.innerHTML = trend.map(d => {
    const heightPct = Math.max((d.count / max) * 140, 4);
    return `
      <div class="bar-wrap fade-in">
        <div class="bar__num">${d.count}</div>
        <div class="bar" style="height:${heightPct}px" title="${d.day}: ${d.count} signups"></div>
        <div class="bar__label">${d.day}</div>
      </div>
    `;
  }).join("");
}

/* ── Load all stats ───────────────────────────────────────────────────────── */
async function loadStats() {
  try {
    const res  = await fetch(`${API}/stats`, { signal: AbortSignal.timeout(8000) });

    if (!res.ok) throw new Error(`Server responded with ${res.status}`);

    const data = await res.json();

    // Animate main counters
    const cards = [
      { id: "totalUsers",     val: data.total_users      ?? 0 },
      { id: "loginsToday",    val: data.logins_today     ?? 0 },
      { id: "totalCompanies", val: data.total_companies  ?? 0 },
      { id: "loginsTotal",    val: data.total_logins     ?? 0 },
    ];

    cards.forEach(({ id, val }) => {
      const el = document.querySelector(`#${id} .counter`);
      if (el) animateCounter(el, val);
    });

    // Recent signups table
    renderTable(data.recent_users ?? []);

    // 7-day trend bar chart
    renderBarChart(data.trend_7d ?? []);

  } catch (err) {
    console.error("Stats load error:", err);

    // Show friendly zero-state
    ["totalUsers", "loginsToday", "totalCompanies", "loginsTotal"].forEach(id => {
      const el = document.querySelector(`#${id} .counter`);
      if (el) el.textContent = "—";
    });

    document.getElementById("recentBody").innerHTML =
      `<tr><td colspan="4" class="table-loading" style="color:#EF4444">
        ⚠️ Could not load stats. Make sure the backend server is running.
      </td></tr>`;

    document.getElementById("barChart").innerHTML =
      `<div class="bar-chart__loading" style="color:#EF4444">Backend connection failed.</div>`;
  }
}

/* ── Helpers ──────────────────────────────────────────────────────────────── */
function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function formatDate(iso) {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString("en-IN", {
      day: "2-digit", month: "short", year: "numeric",
      hour: "2-digit", minute: "2-digit",
    });
  } catch { return iso; }
}

/* ── Init ─────────────────────────────────────────────────────────────────── */
loadStats();

// Auto-refresh every 30 seconds
setInterval(loadStats, 30_000);
