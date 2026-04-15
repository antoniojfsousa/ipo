/* dashboard.js — NF-IPO Lisboa */

const API = "";

async function apiFetch(path, options = {}) {
  const res = await fetch(API + path, options);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

// ── Dashboard load ──────────────────────────────────────────
async function loadDashboard() {
  try {
    const summary = await apiFetch("/api/alerts/dashboard");
    document.getElementById("statTotalPatients").textContent = summary.total_patients;
    document.getElementById("statActiveAlerts").textContent = summary.active_alerts;
    document.getElementById("statPendingSuggestions").textContent = summary.pending_suggestions;
    document.getElementById("statNoConsent").textContent = summary.patients_without_consent;

    if (summary.critical_alerts > 0) {
      document.getElementById("statActiveAlerts").closest(".stat-card").querySelector(".stat-icon").classList.add("text-danger");
    }
  } catch (e) {
    console.error("Erro ao carregar dashboard:", e);
  }
}

// ── Alerts ──────────────────────────────────────────────────
async function loadAlerts() {
  const container = document.getElementById("alertsContainer");
  container.innerHTML = '<div class="text-center text-muted py-3"><i class="fa-solid fa-spinner fa-spin me-2"></i>A carregar…</div>';
  try {
    const alerts = await apiFetch("/api/alerts?status=ativo&limit=30");
    if (!alerts.length) {
      container.innerHTML = '<div class="text-center text-success py-3"><i class="fa-solid fa-check-circle me-2"></i>Sem alertas ativos.</div>';
      return;
    }
    const grouped = { critica: [], alta: [], media: [], baixa: [] };
    alerts.forEach(a => {
      if (grouped[a.prioridade]) grouped[a.prioridade].push(a);
      else grouped.baixa.push(a);
    });
    const labels = { critica: "Crítica", alta: "Alta", media: "Média", baixa: "Baixa" };
    let html = "";
    for (const [prio, items] of Object.entries(grouped)) {
      if (!items.length) continue;
      html += `<div class="mb-3"><div class="fw-semibold text-uppercase small mb-2" style="letter-spacing:.06em">${labels[prio]}</div>`;
      items.forEach(a => {
        html += `
          <div class="p-2 mb-2 rounded alert-${prio}" style="font-size:.9rem;">
            <div class="d-flex justify-content-between align-items-start">
              <div>
                <span class="badge badge-${prio} me-1">${labels[prio]}</span>
                <strong>${escHtml(a.titulo)}</strong>
                ${a.patient_nome ? `<span class="text-muted ms-1">— ${escHtml(a.patient_nome)} (${escHtml(a.patient_processo || "")})</span>` : ""}
              </div>
              <div class="d-flex gap-1 ms-2">
                <button class="btn btn-sm btn-outline-secondary py-0 px-1" title="Em análise" onclick="updateAlert(${a.id},'em_analise')">
                  <i class="fa-solid fa-eye fa-xs"></i>
                </button>
                <button class="btn btn-sm btn-outline-success py-0 px-1" title="Resolver" onclick="updateAlert(${a.id},'resolvido')">
                  <i class="fa-solid fa-check fa-xs"></i>
                </button>
              </div>
            </div>
            ${a.descricao ? `<div class="text-muted mt-1" style="font-size:.8rem;">${escHtml(a.descricao)}</div>` : ""}
            <div class="text-muted mt-1" style="font-size:.75rem;">
              ${a.patient_processo ? `<a href="/patients-view?id=${a.patient_id}" class="text-decoration-none text-primary">Ver doente</a> ·` : ""}
              ${a.data_criacao}
            </div>
          </div>`;
      });
      html += "</div>";
    }
    container.innerHTML = html;
  } catch (e) {
    container.innerHTML = `<div class="text-danger py-2"><i class="fa-solid fa-circle-exclamation me-1"></i>${escHtml(e.message)}</div>`;
  }
}

async function updateAlert(id, status) {
  try {
    await apiFetch(`/api/alerts/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
    });
    loadAlerts();
    loadDashboard();
  } catch (e) {
    alert("Erro: " + e.message);
  }
}

async function runChecks() {
  try {
    const res = await apiFetch("/api/alerts/run-checks", { method: "POST" });
    alert(`Verificação concluída: ${res.alerts_created} novos alertas gerados para ${res.patients_checked} doentes.`);
    loadAlerts();
    loadDashboard();
  } catch (e) {
    alert("Erro: " + e.message);
  }
}

// ── Suggestions ──────────────────────────────────────────────
async function loadSuggestions() {
  const container = document.getElementById("suggestionsContainer");
  try {
    const sugs = await apiFetch("/api/suggestions?status=pendente");
    if (!sugs.length) {
      container.innerHTML = '<div class="text-center text-success py-3"><i class="fa-solid fa-check-circle me-2"></i>Sem sugestões pendentes.</div>';
      return;
    }
    container.innerHTML = sugs.map(s => `
      <div class="suggestion-card">
        <div class="d-flex justify-content-between align-items-start">
          <div>
            <span class="badge bg-info source-badge me-1">${escHtml(s.fonte)}</span>
            <strong>${escHtml(s.titulo)}</strong>
          </div>
          <div class="d-flex gap-1">
            <button class="btn btn-sm btn-success py-0 px-2" onclick="validateSuggestion(${s.id},'aprovado')">
              <i class="fa-solid fa-check fa-xs me-1"></i>Aprovar
            </button>
            <button class="btn btn-sm btn-danger py-0 px-2" onclick="validateSuggestion(${s.id},'rejeitado')">
              <i class="fa-solid fa-xmark fa-xs me-1"></i>Rejeitar
            </button>
          </div>
        </div>
        ${s.descricao ? `<div class="text-muted mt-1" style="font-size:.85rem;">${escHtml(s.descricao)}</div>` : ""}
        <div class="text-muted mt-1" style="font-size:.75rem;">
          <a href="/patients-view?id=${s.patient_id}" class="text-decoration-none text-primary">Ver doente</a>
        </div>
      </div>`).join("");
  } catch (e) {
    container.innerHTML = `<div class="text-danger py-2">${escHtml(e.message)}</div>`;
  }
}

async function validateSuggestion(id, status) {
  try {
    await apiFetch(`/api/suggestions/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status, validado_por: "Utilizador" }),
    });
    loadSuggestions();
    loadDashboard();
  } catch (e) {
    alert("Erro: " + e.message);
  }
}

// ── Patient search ────────────────────────────────────────────
async function searchPatients() {
  const q = document.getElementById("searchInput").value.trim();
  if (!q) { loadAllPatients(); return; }
  try {
    const patients = await apiFetch(`/api/patients?search=${encodeURIComponent(q)}&limit=20`);
    renderPatients(patients);
  } catch (e) {
    document.getElementById("patientResults").innerHTML = `<div class="text-danger">${escHtml(e.message)}</div>`;
  }
}

async function loadAllPatients() {
  try {
    const patients = await apiFetch("/api/patients?limit=50");
    renderPatients(patients);
  } catch (e) {
    document.getElementById("patientResults").innerHTML = `<div class="text-danger">${escHtml(e.message)}</div>`;
  }
}

function renderPatients(patients) {
  const el = document.getElementById("patientResults");
  if (!patients.length) {
    el.innerHTML = '<div class="text-muted small text-center py-2">Nenhum doente encontrado.</div>';
    return;
  }
  el.innerHTML = `<div class="list-group list-group-flush">` +
    patients.map(p => `
      <a href="/patients-view?id=${p.id}" class="list-group-item list-group-item-action patient-row py-2">
        <div class="d-flex justify-content-between">
          <div>
            <div class="fw-semibold">${escHtml(p.nome_completo)}</div>
            <div class="text-muted small">Proc. ${escHtml(p.numero_processo)} · ${escHtml(p.data_nascimento)}</div>
          </div>
          <span class="badge ${p.nf1_confirmado ? 'bg-primary' : 'bg-secondary'} align-self-center" style="font-size:.7rem;">
            ${p.nf1_confirmado ? 'NF1 ✓' : 'NF1 ?'}
          </span>
        </div>
      </a>`).join("") +
    `</div>`;
}

// ── New patient form ──────────────────────────────────────────
async function submitNewPatient() {
  const form = document.getElementById("formNewPatient");
  const data = Object.fromEntries(new FormData(form));
  data.nf1_confirmado = form.querySelector('[name="nf1_confirmado"]').checked;
  try {
    await apiFetch("/api/patients", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    bootstrap.Modal.getInstance(document.getElementById("modalNewPatient")).hide();
    form.reset();
    loadDashboard();
    loadAllPatients();
  } catch (e) {
    alert("Erro ao criar doente: " + e.message);
  }
}

// ── Search on enter ───────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  loadDashboard();
  loadAlerts();
  loadSuggestions();
  document.getElementById("searchInput").addEventListener("keydown", e => {
    if (e.key === "Enter") searchPatients();
  });
});

function escHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
