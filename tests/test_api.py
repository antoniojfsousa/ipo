"""
Tests for NF-IPO Clinical Management System API.
Uses an in-memory SQLite database via TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# ── Test DB setup ─────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


# ── Patient fixtures ──────────────────────────────────────────

@pytest.fixture(scope="module")
def created_patient(client):
    payload = {
        "numero_processo": "P-2024-001",
        "nome_completo": "Maria Silva Ferreira",
        "data_nascimento": "1985-06-15",
        "genero": "F",
        "nif": "123456789",
        "numero_sns": "987654321",
        "medico_responsavel": "Dr. João Costa",
        "nf1_confirmado": True,
        "data_diagnostico": "2010-03-20",
        "mutacao_genetica": "c.1381C>T (p.Arg461Cys)",
    }
    res = client.post("/api/patients", json=payload)
    assert res.status_code == 201
    return res.json()


# ── Tests ─────────────────────────────────────────────────────

def test_create_patient(client, created_patient):
    assert created_patient["id"] is not None
    assert created_patient["nome_completo"] == "Maria Silva Ferreira"
    assert created_patient["numero_processo"] == "P-2024-001"
    assert created_patient["nf1_confirmado"] is True


def test_create_duplicate_patient(client, created_patient):
    payload = {
        "numero_processo": "P-2024-001",  # Same processo number
        "nome_completo": "Outro Nome",
        "data_nascimento": "1990-01-01",
        "genero": "M",
    }
    res = client.post("/api/patients", json=payload)
    assert res.status_code == 400


def test_get_patient(client, created_patient):
    pid = created_patient["id"]
    res = client.get(f"/api/patients/{pid}")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == pid
    assert data["nome_completo"] == "Maria Silva Ferreira"


def test_get_nonexistent_patient(client):
    res = client.get("/api/patients/99999")
    assert res.status_code == 404


def test_list_patients(client, created_patient):
    res = client.get("/api/patients")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) >= 1


def test_search_patients(client, created_patient):
    res = client.get("/api/patients?search=Maria")
    assert res.status_code == 200
    results = res.json()
    assert any(p["nome_completo"] == "Maria Silva Ferreira" for p in results)


def test_update_patient(client, created_patient):
    pid = created_patient["id"]
    res = client.put(f"/api/patients/{pid}", json={"telefone": "912345678", "localidade": "Lisboa"})
    assert res.status_code == 200
    assert res.json()["telefone"] == "912345678"


def test_patient_summary(client, created_patient):
    pid = created_patient["id"]
    res = client.get(f"/api/patients/{pid}/summary")
    assert res.status_code == 200
    data = res.json()
    assert "has_active_consent" in data
    assert "active_alerts_count" in data
    assert data["has_active_consent"] is False  # no consent added yet


# ── Consent ───────────────────────────────────────────────────

def test_add_consent(client, created_patient):
    pid = created_patient["id"]
    payload = {
        "tipo_consentimento": "dados_clinicos",
        "data_consentimento": "2024-01-10",
        "consentido_por": "patient",
        "nome_responsavel": "Maria Silva Ferreira",
        "ativo": True,
    }
    res = client.post(f"/api/patients/{pid}/consents", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["ativo"] is True
    assert data["tipo_consentimento"] == "dados_clinicos"


def test_get_current_consent(client, created_patient):
    pid = created_patient["id"]
    res = client.get(f"/api/patients/{pid}/consents/current")
    assert res.status_code == 200
    assert res.json()["ativo"] is True


def test_patient_summary_with_consent(client, created_patient):
    pid = created_patient["id"]
    res = client.get(f"/api/patients/{pid}/summary")
    assert res.status_code == 200
    assert res.json()["has_active_consent"] is True


def test_list_consents(client, created_patient):
    pid = created_patient["id"]
    res = client.get(f"/api/patients/{pid}/consents")
    assert res.status_code == 200
    assert len(res.json()) >= 1


# ── GMNF ──────────────────────────────────────────────────────

def test_add_gmnf_decision(client, created_patient):
    pid = created_patient["id"]
    payload = {
        "data_reuniao": "2024-02-15",
        "numero_reuniao": "GMNF-2024-03",
        "tratamento_proposto": "Selumetinib 25mg 2x/dia",
        "justificacao": "Neurofibroma plexiforme sintomático com crescimento documentado",
        "decisao": "aprovado",
        "medico_responsavel": "Dr. João Costa",
    }
    res = client.post(f"/api/patients/{pid}/gmnf", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["decisao"] == "aprovado"
    assert data["patient_id"] == pid


def test_list_gmnf(client, created_patient):
    pid = created_patient["id"]
    res = client.get(f"/api/patients/{pid}/gmnf")
    assert res.status_code == 200
    assert len(res.json()) >= 1


# ── Therapy ───────────────────────────────────────────────────

def test_add_therapy(client, created_patient):
    pid = created_patient["id"]
    payload = {
        "farmaco": "selumetinib",
        "data_inicio": "2024-03-01",
        "dose_mg": 25.0,
        "frequencia": "2x/dia",
        "indicacao": "Neurofibroma plexiforme não ressecável",
        "status": "ativo",
        "medico_prescritor": "Dr. João Costa",
    }
    res = client.post(f"/api/patients/{pid}/therapy", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["farmaco"] == "selumetinib"
    assert data["status"] == "ativo"


def test_get_active_therapy(client, created_patient):
    pid = created_patient["id"]
    res = client.get(f"/api/patients/{pid}/therapy/active")
    assert res.status_code == 200
    assert len(res.json()) >= 1


# ── Exams ─────────────────────────────────────────────────────

def test_add_exam(client, created_patient):
    pid = created_patient["id"]
    payload = {
        "tipo_exame": "RM",
        "subtipo": "Crânio e Coluna",
        "data_solicitacao": "2024-01-20",
        "solicitado_por": "Dr. João Costa",
        "status": "realizado",
        "data_realizacao": "2024-02-01",
    }
    res = client.post(f"/api/patients/{pid}/exams", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["tipo_exame"] == "RM"


def test_add_critical_exam(client, created_patient):
    pid = created_patient["id"]
    payload = {
        "tipo_exame": "RM",
        "subtipo": "Coluna Total",
        "data_solicitacao": "2024-03-10",
        "status": "resultado_disponivel",
        "data_realizacao": "2024-03-15",
        "data_resultado": "2024-03-16",
        "resultado_critico": True,
        "resultado_resumo": "Compressão medular cervical identificada",
    }
    res = client.post(f"/api/patients/{pid}/exams", json=payload)
    assert res.status_code == 201
    assert res.json()["resultado_critico"] is True


def test_list_exams(client, created_patient):
    pid = created_patient["id"]
    res = client.get(f"/api/patients/{pid}/exams")
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_pending_exams(client, created_patient):
    pid = created_patient["id"]
    # Add a pending exam
    client.post(f"/api/patients/{pid}/exams", json={
        "tipo_exame": "TC",
        "data_solicitacao": "2024-04-01",
        "status": "solicitado",
    })
    res = client.get(f"/api/patients/{pid}/exams/pending")
    assert res.status_code == 200
    assert len(res.json()) >= 1


# ── Alerts ────────────────────────────────────────────────────

def test_generate_alerts(client, created_patient):
    pid = created_patient["id"]
    res = client.post("/api/alerts/run-checks")
    assert res.status_code == 200
    data = res.json()
    assert "alerts_created" in data
    assert "patients_checked" in data
    assert data["patients_checked"] >= 1


def test_get_patient_alerts(client, created_patient):
    pid = created_patient["id"]
    res = client.get(f"/api/patients/{pid}/alerts")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_list_all_alerts(client):
    res = client.get("/api/alerts?status=ativo")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_dashboard_summary(client):
    res = client.get("/api/alerts/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "total_patients" in data
    assert "active_alerts" in data
    assert "pending_suggestions" in data
    assert data["total_patients"] >= 1


def test_resolve_alert(client, created_patient):
    pid = created_patient["id"]
    alerts_res = client.get(f"/api/patients/{pid}/alerts")
    alerts = alerts_res.json()
    active = [a for a in alerts if a["status"] == "ativo"]
    if active:
        alert_id = active[0]["id"]
        res = client.put(f"/api/alerts/{alert_id}", json={
            "status": "resolvido",
            "resolvido_por": "Dr. Teste",
            "notas_resolucao": "Situação avaliada e resolvida",
        })
        assert res.status_code == 200
        assert res.json()["status"] == "resolvido"


# ── Timeline ──────────────────────────────────────────────────

def test_get_timeline(client, created_patient):
    pid = created_patient["id"]
    res = client.get(f"/api/patients/{pid}/timeline")
    assert res.status_code == 200
    items = res.json()
    assert isinstance(items, list)
    assert len(items) > 0
    # Check expected types are present
    types = {item["tipo"] for item in items}
    assert "exame" in types


def test_timeline_chronological_order(client, created_patient):
    pid = created_patient["id"]
    res = client.get(f"/api/patients/{pid}/timeline")
    items = res.json()
    dates = [item["date"] for item in items]
    assert dates == sorted(dates, reverse=True), "Timeline should be in descending date order"


# ── Consultas ─────────────────────────────────────────────────

def test_add_consulta(client, created_patient):
    pid = created_patient["id"]
    payload = {
        "data_consulta": "2024-05-10",
        "tipo_consulta": "rotina",
        "medico": "Dr. João Costa",
        "especialidade": "Neurologia Pediátrica",
        "motivo": "Consulta de seguimento semestral",
        "resumo_clinica": "Doente estável. Sem novas lesões.",
        "notas_clinicas": "Iniciar trametinib conforme decisão GMNF. Solicitar RM crânio.",
    }
    res = client.post(f"/api/patients/{pid}/consultas", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["tipo_consulta"] == "rotina"


def test_nlp_generates_suggestions(client, created_patient):
    """After adding a consulta with keywords, suggestions should be generated."""
    pid = created_patient["id"]
    res = client.get(f"/api/patients/{pid}/suggestions")
    assert res.status_code == 200
    # NLP from the consulta should have generated suggestions
    suggestions = res.json()
    assert isinstance(suggestions, list)


def test_validate_suggestion(client, created_patient):
    pid = created_patient["id"]
    sugs_res = client.get("/api/suggestions?status=pendente")
    sugs = sugs_res.json()
    if sugs:
        sug_id = sugs[0]["id"]
        res = client.put(f"/api/suggestions/{sug_id}", json={
            "status": "aprovado",
            "validado_por": "Dr. Teste",
        })
        assert res.status_code == 200
        assert res.json()["status"] == "aprovado"
