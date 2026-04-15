/* patient.js — NF-IPO Lisboa */

const API = "";
let PATIENT_ID = null;

function escHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

async function apiFetch(path, options = {}) {
  const res = await fetch(API + path, options);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

function getPatientId() {
  const params = new URLSearchParams(window.location.search);
  return params.get("id");
}

// ── Patient Header ──────────────────────────────────────────
async function loadPatientHeader(id) {
  const card = document.getElementById("patientHeader");
  try {
    const [patient, summary] = await Promise.all([
      apiFetch(`/api/patients/${id}`),
      apiFetch(`/api/patients/${id}/summary`),
    ]);
    document.title = `${patient.nome_completo} — NF-IPO Lisboa`;
    card.innerHTML = `
      <div class="card-body">
        <div class="row align-items-center">
          <div class="col-md-8">
            <h4 class="mb-1 fw-bold">${escHtml(patient.nome_completo)}</h4>
            <div class="text-muted mb-2">
              <span class="me-3"><i class="fa-solid fa-id-card me-1"></i>Proc. <strong>${escHtml(patient.numero_processo)}</strong></span>
              <span class="me-3"><i class="fa-solid fa-cake-candles me-1"></i>${escHtml(patient.data_nascimento)}</span>
              <span class="me-3"><i class="fa-solid fa-venus-mars me-1"></i>${escHtml(patient.genero)}</span>
              ${patient.telefone ? `<span><i class="fa-solid fa-phone me-1"></i>${escHtml(patient.telefone)}</span>` : ""}
            </div>
            <div class="d-flex flex-wrap gap-2">
              <span class="badge ${patient.nf1_confirmado ? 'bg-primary' : 'bg-secondary'}">
                <i class="fa-solid fa-dna me-1"></i>NF1 ${patient.nf1_confirmado ? 'Confirmado' : 'Não Confirmado'}
              </span>
              ${patient.medico_responsavel ? `<span class="badge bg-light text-dark border"><i class="fa-solid fa-user-md me-1"></i>${escHtml(patient.medico_responsavel)}</span>` : ""}
              <span class="badge ${summary.has_active_consent ? 'bg-success' : 'bg-danger'}">
                <i class="fa-solid fa-file-signature me-1"></i>${summary.has_active_consent ? 'Consentimento Ativo' : 'Sem Consentimento'}
              </span>
              ${summary.active_alerts_count > 0 ? `<span class="badge bg-warning text-dark"><i class="fa-solid fa-bell me-1"></i>${summary.active_alerts_count} Alertas</span>` : ""}
            </div>
          </div>
          <div class="col-md-4 text-md-end mt-3 mt-md-0">
            ${patient.mutacao_genetica ? `<div class="text-muted small mb-1"><i class="fa-solid fa-virus me-1"></i>Mutação: <strong>${escHtml(patient.mutacao_genetica)}</strong></div>` : ""}
            ${patient.data_diagnostico ? `<div class="text-muted small mb-1"><i class="fa-solid fa-calendar me-1"></i>Diagnóstico: <strong>${escHtml(patient.data_diagnostico)}</strong></div>` : ""}
            ${summary.last_consulta ? `<div class="text-muted small"><i class="fa-solid fa-clock me-1"></i>Última consulta: <strong>${escHtml(summary.last_consulta)}</strong></div>` : ""}
          </div>
        </div>
      </div>`;
  } catch (e) {
    card.innerHTML = `<div class="card-body text-danger"><i class="fa-solid fa-circle-exclamation me-2"></i>Erro: ${escHtml(e.message)}</div>`;
  }
}

// ── Consent ─────────────────────────────────────────────────
async function loadConsent(id) {
  const body = document.getElementById("consentBody");
  try {
    const consent = await apiFetch(`/api/patients/${id}/consents/current`);
    body.innerHTML = `
      <div class="consent-active"><i class="fa-solid fa-circle-check me-2"></i>Consentimento Ativo</div>
      <div class="text-muted small mt-1">Tipo: ${escHtml(consent.tipo_consentimento)}</div>
      <div class="text-muted small">Data: ${escHtml(consent.data_consentimento)}</div>
      ${consent.validade_ate ? `<div class="text-muted small">Validade: ${escHtml(consent.validade_ate)}</div>` : ""}
      <div class="text-muted small">Assinado por: ${escHtml(consent.nome_responsavel)}</div>`;
  } catch {
    body.innerHTML = `
      <div class="consent-missing"><i class="fa-solid fa-circle-xmark me-2"></i>Sem Consentimento Ativo</div>
      <button class="btn btn-sm btn-outline-danger mt-2" onclick="openConsentModal()">
        <i class="fa-solid fa-plus me-1"></i>Registar Consentimento
      </button>`;
  }
}

// ── Timeline ─────────────────────────────────────────────────
const TIMELINE_ICONS = {
  consulta:    { icon: "fa-stethoscope",  cls: "consulta" },
  gmnf:        { icon: "fa-users",        cls: "gmnf" },
  exame:       { icon: "fa-microscope",   cls: "exame" },
  terapeutica: { icon: "fa-pills",        cls: "terapeutica" },
};

const STATUS_LABELS = {
  ativo: "Ativo", suspenso: "Suspenso", terminado: "Terminado", aguarda_inicio: "Aguarda Início",
  solicitado: "Solicitado", agendado: "Agendado", realizado: "Realizado",
  resultado_disponivel: "Resultado Disponível", cancelado: "Cancelado",
  aprovado: "Aprovado", recusado: "Recusado", pendente: "Pendente", aguarda_exames: "Aguarda Exames",
  rotina: "Rotina", urgencia: "Urgência", gmnf: "GMNF", seguimento: "Seguimento",
};

function statusBadge(status) {
  const label = STATUS_LABELS[status] || status || "";
  const colorMap = {
    ativo: "bg-success", aprovado: "bg-success", realizado: "bg-success", resultado_disponivel: "bg-info",
    suspenso: "bg-warning text-dark", pendente: "bg-warning text-dark", agendado: "bg-info",
    terminado: "bg-secondary", cancelado: "bg-secondary", recusado: "bg-danger",
    aguarda_exames: "bg-secondary", aguarda_inicio: "bg-light text-dark border",
    solicitado: "bg-primary",
  };
  const cls = colorMap[status] || "bg-secondary";
  return `<span class="badge ${cls}" style="font-size:.7rem;">${escHtml(label)}</span>`;
}

async function loadTimeline(id) {
  const container = document.getElementById("timelineContainer");
  try {
    const items = await apiFetch(`/api/patients/${id}/timeline`);
    if (!items.length) {
      container.innerHTML = '<div class="text-muted text-center py-4">Nenhum evento registado.</div>';
      return;
    }
    let html = '<div class="timeline">';
    items.forEach(item => {
      const info = TIMELINE_ICONS[item.tipo] || { icon: "fa-circle", cls: "consulta" };
      const criticalBadge = item.extra && item.extra.resultado_critico
        ? `<span class="badge bg-danger ms-1" style="font-size:.7rem;">CRÍTICO</span>` : "";
      html += `
        <div class="timeline-item">
          <div class="timeline-icon ${info.cls}">
            <i class="fa-solid ${info.icon}"></i>
          </div>
          <div class="timeline-card ${info.cls}">
            <div class="d-flex justify-content-between align-items-start flex-wrap gap-1">
              <strong style="font-size:.9rem;">${escHtml(item.titulo)}${criticalBadge}</strong>
              <div class="d-flex align-items-center gap-1">
                ${item.status ? statusBadge(item.status) : ""}
                <span class="text-muted" style="font-size:.75rem;">${escHtml(item.date)}</span>
              </div>
            </div>
            ${item.descricao ? `<div class="text-muted mt-1" style="font-size:.82rem;">${escHtml(item.descricao)}</div>` : ""}
            ${renderExtra(item)}
          </div>
        </div>`;
    });
    html += "</div>";
    container.innerHTML = html;
  } catch (e) {
    container.innerHTML = `<div class="text-danger py-2">${escHtml(e.message)}</div>`;
  }
}

function renderExtra(item) {
  if (!item.extra) return "";
  const parts = [];
  if (item.extra.especialidade) parts.push(`Especialidade: ${escHtml(item.extra.especialidade)}`);
  if (item.extra.proxima_consulta) parts.push(`Próxima consulta: ${escHtml(item.extra.proxima_consulta)}`);
  if (item.extra.dose_mg) parts.push(`Dose: ${item.extra.dose_mg} mg`);
  if (item.extra.frequencia) parts.push(`Frequência: ${escHtml(item.extra.frequencia)}`);
  if (item.extra.avaliacao_resposta) parts.push(`Resposta: ${escHtml(item.extra.avaliacao_resposta)}`);
  if (item.extra.solicitado_por) parts.push(`Solicitado por: ${escHtml(item.extra.solicitado_por)}`);
  if (!parts.length) return "";
  return `<div class="text-muted mt-1" style="font-size:.78rem;">${parts.join(" · ")}</div>`;
}

// ── Patient Alerts ────────────────────────────────────────────
async function loadPatientAlerts(id) {
  const container = document.getElementById("patientAlertsContainer");
  try {
    const alerts = await apiFetch(`/api/patients/${id}/alerts`);
    const active = alerts.filter(a => ["ativo", "em_analise"].includes(a.status));
    if (!active.length) {
      container.innerHTML = '<div class="text-success small"><i class="fa-solid fa-check-circle me-1"></i>Sem alertas ativos.</div>';
      return;
    }
    container.innerHTML = active.map(a => `
      <div class="p-2 mb-2 rounded alert-${a.prioridade}" style="font-size:.85rem;">
        <div class="d-flex justify-content-between">
          <strong>${escHtml(a.titulo)}</strong>
          <span class="badge badge-${a.prioridade}">${escHtml(a.prioridade)}</span>
        </div>
        ${a.descricao ? `<div class="text-muted mt-1" style="font-size:.78rem;">${escHtml(a.descricao)}</div>` : ""}
        <div class="mt-1">
          <button class="btn btn-sm btn-outline-success py-0 px-1" onclick="resolveAlert(${a.id})">
            <i class="fa-solid fa-check fa-xs"></i> Resolver
          </button>
        </div>
      </div>`).join("");
  } catch (e) {
    container.innerHTML = `<div class="text-danger small">${escHtml(e.message)}</div>`;
  }
}

async function resolveAlert(alertId) {
  try {
    await apiFetch(`/api/alerts/${alertId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: "resolvido", resolvido_por: "Utilizador" }),
    });
    loadPatientAlerts(PATIENT_ID);
    loadPatientHeader(PATIENT_ID);
  } catch (e) {
    alert("Erro: " + e.message);
  }
}

// ── Active Therapy ────────────────────────────────────────────
async function loadActiveTherapy(id) {
  const container = document.getElementById("activeTherapyContainer");
  try {
    const items = await apiFetch(`/api/patients/${id}/therapy/active`);
    if (!items.length) {
      container.innerHTML = '<div class="text-muted small">Sem terapêutica ativa.</div>';
      return;
    }
    container.innerHTML = items.map(t => `
      <div class="mb-2 p-2 bg-light rounded" style="font-size:.85rem;">
        <strong>${escHtml(t.farmaco)}</strong>
        ${t.dose_mg ? `<span class="text-muted ms-1">${t.dose_mg} mg</span>` : ""}
        ${t.frequencia ? `<span class="text-muted ms-1">· ${escHtml(t.frequencia)}</span>` : ""}
        <div class="text-muted" style="font-size:.78rem;">Início: ${escHtml(t.data_inicio)}</div>
        ${t.avaliacao_resposta ? `<div class="text-muted" style="font-size:.78rem;">Resposta: ${escHtml(t.avaliacao_resposta)}</div>` : ""}
      </div>`).join("");
  } catch (e) {
    container.innerHTML = `<div class="text-danger small">${escHtml(e.message)}</div>`;
  }
}

// ── Modal helpers ─────────────────────────────────────────────
function openModal(id) {
  new bootstrap.Modal(document.getElementById(id)).show();
}

function openConsentModal() {
  // Simple inline consent form
  const html = `
    <div class="modal fade" id="modalConsent" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-success text-white">
            <h5 class="modal-title"><i class="fa-solid fa-file-signature me-2"></i>Registar Consentimento</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form id="formConsent">
              <div class="row g-3">
                <div class="col-12">
                  <label class="form-label">Tipo *</label>
                  <select class="form-select" name="tipo_consentimento" required>
                    <option value="dados_clinicos">Dados Clínicos</option>
                    <option value="investigacao">Investigação</option>
                    <option value="ambos">Ambos</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Data *</label>
                  <input type="date" class="form-control" name="data_consentimento" required />
                </div>
                <div class="col-md-6">
                  <label class="form-label">Validade até</label>
                  <input type="date" class="form-control" name="validade_ate" />
                </div>
                <div class="col-md-6">
                  <label class="form-label">Consentido por *</label>
                  <select class="form-select" name="consentido_por" required>
                    <option value="patient">Doente</option>
                    <option value="tutor">Tutor/Responsável</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Nome Responsável *</label>
                  <input type="text" class="form-control" name="nome_responsavel" required />
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
            <button type="button" class="btn btn-success" onclick="submitConsent()">Guardar</button>
          </div>
        </div>
      </div>
    </div>`;
  document.body.insertAdjacentHTML("beforeend", html);
  new bootstrap.Modal(document.getElementById("modalConsent")).show();
}

async function submitConsent() {
  const form = document.getElementById("formConsent");
  const data = Object.fromEntries(new FormData(form));
  try {
    await apiFetch(`/api/patients/${PATIENT_ID}/consents`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    bootstrap.Modal.getInstance(document.getElementById("modalConsent")).hide();
    loadConsent(PATIENT_ID);
    loadPatientHeader(PATIENT_ID);
  } catch (e) {
    alert("Erro: " + e.message);
  }
}

// ── Submit forms ──────────────────────────────────────────────
async function submitConsulta() {
  const form = document.getElementById("formConsulta");
  const data = Object.fromEntries(new FormData(form));
  try {
    await apiFetch(`/api/patients/${PATIENT_ID}/consultas`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    bootstrap.Modal.getInstance(document.getElementById("modalConsulta")).hide();
    form.reset();
    loadTimeline(PATIENT_ID);
    loadPatientHeader(PATIENT_ID);
  } catch (e) {
    alert("Erro: " + e.message);
  }
}

async function submitExame() {
  const form = document.getElementById("formExame");
  const data = Object.fromEntries(new FormData(form));
  try {
    await apiFetch(`/api/patients/${PATIENT_ID}/exams`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    bootstrap.Modal.getInstance(document.getElementById("modalExame")).hide();
    form.reset();
    loadTimeline(PATIENT_ID);
  } catch (e) {
    alert("Erro: " + e.message);
  }
}

async function submitGmnf() {
  const form = document.getElementById("formGmnf");
  const data = Object.fromEntries(new FormData(form));
  try {
    await apiFetch(`/api/patients/${PATIENT_ID}/gmnf`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    bootstrap.Modal.getInstance(document.getElementById("modalGmnf")).hide();
    form.reset();
    loadTimeline(PATIENT_ID);
  } catch (e) {
    alert("Erro: " + e.message);
  }
}

async function submitTerapia() {
  const form = document.getElementById("formTerapia");
  const data = Object.fromEntries(new FormData(form));
  if (data.dose_mg) data.dose_mg = parseFloat(data.dose_mg);
  try {
    await apiFetch(`/api/patients/${PATIENT_ID}/therapy`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    bootstrap.Modal.getInstance(document.getElementById("modalTerapia")).hide();
    form.reset();
    loadTimeline(PATIENT_ID);
    loadActiveTherapy(PATIENT_ID);
  } catch (e) {
    alert("Erro: " + e.message);
  }
}

// ── Init ──────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  PATIENT_ID = getPatientId();
  if (!PATIENT_ID) {
    document.getElementById("patientHeader").innerHTML =
      '<div class="card-body text-danger"><i class="fa-solid fa-circle-exclamation me-2"></i>ID do doente não especificado. <a href="/">Voltar ao Dashboard</a></div>';
    return;
  }
  loadPatientHeader(PATIENT_ID);
  loadConsent(PATIENT_ID);
  loadTimeline(PATIENT_ID);
  loadPatientAlerts(PATIENT_ID);
  loadActiveTherapy(PATIENT_ID);
});
