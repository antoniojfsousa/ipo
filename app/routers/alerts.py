from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.services.alert_service import run_all_alerts

router = APIRouter(tags=["alerts"])


@router.get("/api/alerts", response_model=list[schemas.AlertaResponse])
def list_all_alerts(
    priority: Optional[str] = Query(None),
    tipo: Optional[str] = Query(None),
    status: Optional[str] = Query("ativo"),
    db: Session = Depends(get_db),
):
    query = db.query(models.Alerta)
    if status:
        query = query.filter(models.Alerta.status == status)
    if priority:
        query = query.filter(models.Alerta.prioridade == priority)
    if tipo:
        query = query.filter(models.Alerta.tipo_alerta == tipo)
    alerts = query.order_by(models.Alerta.data_criacao.desc()).all()

    result = []
    for a in alerts:
        patient = db.query(models.Patient).filter(models.Patient.id == a.patient_id).first()
        item = schemas.AlertaResponse.model_validate(a)
        if patient:
            item.patient_nome = patient.nome_completo
            item.patient_processo = patient.numero_processo
        result.append(item)
    return result


@router.get("/api/patients/{patient_id}/alerts", response_model=list[schemas.AlertaResponse])
def list_patient_alerts(patient_id: int, db: Session = Depends(get_db)):
    if not db.query(models.Patient).filter(models.Patient.id == patient_id).first():
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return db.query(models.Alerta).filter(
        models.Alerta.patient_id == patient_id
    ).order_by(models.Alerta.data_criacao.desc()).all()


@router.put("/api/alerts/{alert_id}", response_model=schemas.AlertaResponse)
def update_alert(alert_id: int, data: schemas.AlertaUpdate, db: Session = Depends(get_db)):
    alert = db.query(models.Alerta).filter(models.Alerta.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(alert, field, value)
    db.commit()
    db.refresh(alert)
    return alert


@router.post("/api/alerts/run-checks")
def run_checks(db: Session = Depends(get_db)):
    result = run_all_alerts(db)
    return result


@router.get("/api/alerts/dashboard", response_model=schemas.DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)):
    total_patients = db.query(models.Patient).count()

    active_alerts = db.query(models.Alerta).filter(
        models.Alerta.status.in_(["ativo", "em_analise"])
    ).count()

    critical_alerts = db.query(models.Alerta).filter(
        models.Alerta.status.in_(["ativo", "em_analise"]),
        models.Alerta.prioridade == "critica",
    ).count()

    high_alerts = db.query(models.Alerta).filter(
        models.Alerta.status.in_(["ativo", "em_analise"]),
        models.Alerta.prioridade == "alta",
    ).count()

    pending_suggestions = db.query(models.SugestaoSistema).filter(
        models.SugestaoSistema.status == "pendente"
    ).count()

    # Patients with no active consent
    from sqlalchemy import select as sa_select
    patients_with_consent_select = sa_select(models.InformedConsent.patient_id).where(
        models.InformedConsent.ativo == True
    ).distinct()
    patients_without_consent = db.query(models.Patient).filter(
        ~models.Patient.id.in_(patients_with_consent_select)
    ).count()

    # Alerts by type
    from sqlalchemy import func
    type_counts = db.query(
        models.Alerta.tipo_alerta, func.count(models.Alerta.id)
    ).filter(
        models.Alerta.status.in_(["ativo", "em_analise"])
    ).group_by(models.Alerta.tipo_alerta).all()
    alerts_by_type = {t: c for t, c in type_counts}

    return schemas.DashboardSummary(
        total_patients=total_patients,
        active_alerts=active_alerts,
        critical_alerts=critical_alerts,
        high_alerts=high_alerts,
        pending_suggestions=pending_suggestions,
        patients_without_consent=patients_without_consent,
        alerts_by_type=alerts_by_type,
    )
