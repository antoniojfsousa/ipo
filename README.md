# Sistema de Gestão Clínica NF-IPO Lisboa

Sistema clínico para gestão de doentes com Neurofibromatose tipo 1 (NF1) no Instituto Português de Oncologia de Lisboa.

## Funcionalidades

- **Gestão de Doentes** — Perfil unificado com dados demográficos e clínicos
- **Consentimento Informado** — Módulo de validação ética antes da extração de dados
- **GMNF** — Registo de decisões do Grupo Multidisciplinar de Neurofibromatose
- **Monitorização Terapêutica** — Registo de inibidores MEK (selumetinib, trametinib, etc.)
- **Exames** — Gestão do ciclo de exames médicos
- **Alertas Sentinela** — Sistema automático de alertas (perda de seguimento, exames em atraso, resultados críticos)
- **Painel de Controlo** — Validação de sugestões NLP pelo médico/enfermeiro
- **Linha Cronológica** — Todos os eventos ordenados por data

## Instalação

```bash
pip install -r requirements.txt
```

## Execução

```bash
uvicorn app.main:app --reload
```

Aceda a:
- **Dashboard**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Ficha de Doente**: http://localhost:8000/patients-view?id=1

## Testes

```bash
python -m pytest tests/ -v
```

## Estrutura

```
app/
  main.py           # FastAPI app entry point
  database.py       # SQLAlchemy DB setup (SQLite)
  models.py         # ORM models
  schemas.py        # Pydantic schemas
  routers/          # API routers (patients, alerts, exams, …)
  services/         # Alert service + NLP service
frontend/
  index.html        # Dashboard
  patient.html      # Ficha de doente
  static/           # CSS + JS
tests/
  test_api.py       # pytest tests
```
Sistema Inteligente de Gestão Clínica NF-IPO Lisboa Visão Geral
