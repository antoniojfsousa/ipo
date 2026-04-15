from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/api/patients", tags=["patients"])


@router.get("", response_model=list[schemas.PatientResponse])
def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(models.Patient)
    if search:
        like = f"%{search}%"
        query = query.filter(
            (models.Patient.nome_completo.ilike(like))
            | (models.Patient.numero_processo.ilike(like))
        )
    return query.offset(skip).limit(limit).all()


@router.post("", response_model=schemas.PatientResponse, status_code=201)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Patient).filter(
        models.Patient.numero_processo == patient.numero_processo
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Número de processo já existe")
    db_patient = models.Patient(**patient.model_dump())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@router.get("/{patient_id}", response_model=schemas.PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return patient


@router.put("/{patient_id}", response_model=schemas.PatientResponse)
def update_patient(patient_id: int, data: schemas.PatientUpdate, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("/{patient_id}/summary", response_model=schemas.PatientSummary)
def get_patient_summary(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    has_consent = db.query(models.InformedConsent).filter(
        models.InformedConsent.patient_id == patient_id,
        models.InformedConsent.ativo == True,
    ).first() is not None

    alert_count = db.query(models.Alerta).filter(
        models.Alerta.patient_id == patient_id,
        models.Alerta.status.in_(["ativo", "em_analise"]),
    ).count()

    last_consulta = (
        db.query(models.ConsultaClinica)
        .filter(models.ConsultaClinica.patient_id == patient_id)
        .order_by(models.ConsultaClinica.data_consulta.desc())
        .first()
    )

    return schemas.PatientSummary(
        id=patient.id,
        numero_processo=patient.numero_processo,
        nome_completo=patient.nome_completo,
        data_nascimento=patient.data_nascimento,
        genero=patient.genero,
        nf1_confirmado=patient.nf1_confirmado,
        medico_responsavel=patient.medico_responsavel,
        has_active_consent=has_consent,
        active_alerts_count=alert_count,
        last_consulta=last_consulta.data_consulta if last_consulta else None,
    )
