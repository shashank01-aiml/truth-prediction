/* Owner: A Shashank — frontend. Talks to the FastAPI backend under /api. */
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fmt = h => { const m = Math.round(Math.abs(h) * 60); return `${Math.floor(m / 60)}h ${String(m % 60).padStart(2, "0")}m`; };
const fmtS = s => { const t = Math.floor(s); return [t / 3600 | 0, (t % 3600) / 60 | 0, t % 60].map(v => String(v).padStart(2, "0")).join(":"); };

async function api(method, url, body) {
  const r = await fetch(url, { method, headers: { "Content-Type": "application/json" }, body: body && JSON.stringify(body) });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(Array.isArray(data.detail) ? data.detail[0].msg : (data.detail || r.statusText));
  return data;
}

let current = null;                                 // last prediction, waiting to be tracked
let T = { run: false, acc: 0, t0: 0, tick: null };  // timer state
const elapsed = () => T.acc + (T.run ? (Date.now() - T.t0) / 1000 : 0);

function go(id) {
  document.querySelectorAll("section").forEach(s => s.classList.toggle("on", s.id === id));
  document.querySelectorAll("nav button").forEach(b => b.classList.toggle("on", b.dataset.go === id));
  render();
}

/* ----- Predict ----- */
async function predictNow() {
  if (T.run) { $("pmsg").textContent = "Finish or pause the active task first."; return; }
  try {
    current = await api("POST", "/api/predict", {
      name: $("tn").value, category: $("cat").value, difficulty: $("dif").value,
      experience: $("exp").value, priority: $("pri").value, estimate: +$("est").value });
  } catch (e) { $("pmsg").textContent = e.message; return; }
  resetT(); $("pmsg").textContent = "";
  const p = current, d = p.predicted_hours - p.task.estimate;
  $("res").style.display = "block";
  $("res").innerHTML = `<div class="mut">AI prediction report · ${esc(p.task.name)}</div>
    <div class="big">${fmt(p.predicted_hours)}</div>
    <div class="row">
      <div>Your estimate<br><b>${fmt(p.task.estimate)}</b></div>
      <div>Difference<br><b>${d >= 0 ? "+" : "−"}${fmt(d)}</b></div>
      <div>Personal adjustment<br><b>×${p.factor.toFixed(2)}</b></div>
    </div>
    <p class="mut" style="margin-top:14px">Strongest factors (model contributions vs. an average task):</p>
    <ul>${p.explanation.map(e => `<li>${esc(e.text)} — ${e.hours >= 0 ? "+" : "−"}${Math.abs(e.hours).toFixed(2)} h</li>`).join("")}</ul>
    <p class="note">Base model ${fmt(p.base_hours)}${p.history_count ? `, adjusted with your ${p.history_count} completed tasks (average actual ÷ predicted = ${p.ratio.toFixed(2)})` : " (no personal history yet)"}.</p>
    <button class="p" onclick="go('track')">Start tracking →</button>`;
  paint();
}

/* ----- Tracker ----- */
function startT() {
  if (!current) { $("tmsg").textContent = "Create a prediction first (Predict Time tab)."; return; }
  if (!T.run) { T.run = true; T.t0 = Date.now(); T.tick = setInterval(paint, 250); $("tmsg").textContent = ""; paint(); }
}
function pauseT() { if (T.run) { T.acc += (Date.now() - T.t0) / 1000; T.run = false; clearInterval(T.tick); paint(); } }
function resetT() { clearInterval(T.tick); T = { run: false, acc: 0, t0: 0, tick: null }; }
async function completeT() {
  if (!current) return;
  pauseT();
  if (elapsed() < 1) { $("tmsg").textContent = "Start the task before completing it."; return; }
  try {
    await api("POST", "/api/tasks", { ...current.task, base_hours: current.base_hours,
      predicted_hours: current.predicted_hours, actual_hours: +(elapsed() / 3600).toFixed(4) });
  } catch (e) { $("tmsg").textContent = e.message; return; }
  current = null; resetT(); paint(); go("analytics");
}
function paint() {
  const has = !!current, e = elapsed(), p = has ? current.predicted_hours : 0, pct = p ? (e / 3600) / p * 100 : 0;
  $("tname").textContent = has ? current.task.name : "No active task — create one on the Predict tab";
  $("clock").textContent = fmtS(e);
  $("tbar").style.width = Math.min(100, pct) + "%";
  $("tpct").textContent = has ? `${pct.toFixed(1)}% of predicted duration elapsed${pct > 100 ? " · over prediction" : ""}` : "";
  $("tstat").textContent = !has ? "" : T.run ? "In progress" : e > 0 ? "Paused" : "Ready";
  $("tpred").textContent = has ? fmt(p) : "—";
  $("tact").textContent = has ? fmt(e / 3600) : "—";
  $("bS").disabled = !has || T.run || e > 0;
  $("bP").disabled = !has || !T.run;
  $("bR").disabled = !has || T.run || e === 0;
  $("bC").disabled = !has || e < 1;
}

/* ----- Analytics and history ----- */
function tbl(rows, del) {
  if (!rows.length) return `<p class="mut">No completed tasks yet. Complete a tracked task or load demo data.</p>`;
  return `<table><tr><th>Task</th><th>Category</th><th>Predicted</th><th>Actual</th><th>Error*</th><th>Date</th>${del ? "<th></th>" : ""}</tr>
    ${rows.map(r => { const e = (r.actual_hours - r.predicted_hours) / r.actual_hours * 100; return `<tr><td>${esc(r.name)}</td>
    <td><span class="tag">${esc(r.category)}</span></td><td>${fmt(r.predicted_hours)}</td><td>${fmt(r.actual_hours)}</td>
    <td>${e >= 0 ? "+" : ""}${e.toFixed(0)}%</td><td class="mut">${esc(r.created_at || "")}</td>
    ${del ? `<td><button class="s" onclick="delRow(${r.id})">✕</button></td>` : ""}</tr>`; }).join("")}</table>
    <p class="note">*Positive error = task took longer than predicted.</p>`;
}
function scatter(rows) {
  if (!rows.length) return `<p class="mut">No data yet.</p>`;
  const W = 500, H = 260, p = 40, mx = Math.max(1, ...rows.flatMap(r => [r.predicted_hours, r.actual_hours])) * 1.1;
  const X = v => p + (v / mx) * (W - 2 * p), Y = v => H - p - (v / mx) * (H - 2 * p);
  return `<svg viewBox="0 0 ${W} ${H}">
    <line x1="${X(0)}" y1="${Y(0)}" x2="${X(mx)}" y2="${Y(mx)}" stroke="var(--mut)" stroke-dasharray="4"/>
    <line x1="${p}" y1="${H - p}" x2="${W - p}" y2="${H - p}" stroke="var(--line)"/>
    <line x1="${p}" y1="${p}" x2="${p}" y2="${H - p}" stroke="var(--line)"/>
    <text x="${W / 2}" y="${H - 8}" text-anchor="middle" font-size="12" fill="var(--mut)">Predicted (h)</text>
    <text x="14" y="${H / 2}" font-size="12" fill="var(--mut)" text-anchor="middle" transform="rotate(-90 14 ${H / 2})">Actual (h)</text>
    ${rows.map(r => `<circle cx="${X(r.predicted_hours)}" cy="${Y(r.actual_hours)}" r="5"
      fill="${Math.abs(r.actual_hours - r.predicted_hours) / r.actual_hours <= 0.2 ? "var(--ok)" : "var(--warn)"}">
      <title>${esc(r.name)}: predicted ${fmt(r.predicted_hours)}, actual ${fmt(r.actual_hours)}</title></circle>`).join("")}
    </svg><p class="note">Green = within ±20% of actual. Points above the dashed line took longer than predicted.</p>`;
}
async function render() {
  try {
    const [S, H] = await Promise.all([api("GET", "/api/stats"), api("GET", "/api/tasks")]);
    $("kpis").innerHTML = [
      [S.count, "Completed tasks"],
      [S.avg_error_hours == null ? "—" : fmt(S.avg_error_hours), "Avg prediction error"],
      [S.model_report[1].MAE.toFixed(2) + " h", "Model MAE (holdout)"],
      [S.count ? S.within_20_percent + "%" : "—", "Within ±20% of actual"],
      ["×" + S.factor.toFixed(2), "Personal adjustment"],
    ].map(([a, b]) => `<div class="card kpi"><b>${a}</b><span>${b}</span></div>`).join("");
    $("recent").innerHTML = tbl(H.slice(0, 5), false);
    $("mtab").innerHTML = `<table><tr><th>Model</th><th>MAE</th><th>RMSE</th><th>R²</th></tr>${S.model_report.map(m =>
      `<tr><td>${m.model}</td><td>${m.MAE.toFixed(2)} h</td><td>${m.RMSE.toFixed(2)} h</td><td>${m.R2.toFixed(2)}</td></tr>`).join("")}</table>`;
    $("scatter").innerHTML = scatter(H);
    $("htab").innerHTML = tbl(H, true);
  } catch (e) {
    $("kpis").innerHTML = `<p class="card">Cannot reach the backend (${esc(e.message)}). Start it with: <code>uvicorn backend.main:app --reload</code></p>`;
  }
}
async function loadDemo() { await api("POST", "/api/demo"); go("analytics"); }
async function delRow(id) { await api("DELETE", `/api/tasks/${id}`); render(); }
async function clearAll() { if (confirm("Delete all completed tasks?")) { await api("DELETE", "/api/tasks"); render(); } }

Object.assign(window, { go, predictNow, startT, pauseT, completeT, loadDemo, delRow, clearAll });
paint(); go("dash");
