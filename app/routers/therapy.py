from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter(tags=["therapy"])


def _check_patient(db: Session, patient_id: int):
    if not db.query(models.Patient).filter(models.Patient.id == patient_id).first():
        raise HTTPException(status_code=404, detail="Paciente não encontrado")


@router.get("/api/patients/{patient_id}/therapy", response_model=list[schemas.MonitorizacaoTerapeuticaResponse])
def list_therapy(patient_id: int, db: Session = Depends(get_db)):
    _check_patient(db, patient_id)
    return db.query(models.MonitorizacaoTerapeutica).filter(
        models.MonitorizacaoTerapeutica.patient_id == patient_id
    ).order_by(models.MonitorizacaoTerapeutica.data_inicio.desc()).all()


@router.post("/api/patients/{patient_id}/therapy", response_model=schemas.MonitorizacaoTerapeuticaResponse, status_code=201)
def create_therapy(patient_id: int, data: schemas.MonitorizacaoTerapeuticaCreate, db: Session = Depends(get_db)):
    _check_patient(db, patient_id)
    record = models.MonitorizacaoTerapeutica(patient_id=patient_id, **data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.put("/api/therapy/{therapy_id}", response_model=schemas.MonitorizacaoTerapeuticaResponse)
def update_therapy(therapy_id: int, data: schemas.MonitorizacaoTerapeuticaUpdate, db: Session = Depends(get_db)):
    record = db.query(models.MonitorizacaoTerapeutica).filter(
        models.MonitorizacaoTerapeutica.id == therapy_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Registo terapêutico não encontrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


@router.get("/api/patients/{patient_id}/therapy/active", response_model=list[schemas.MonitorizacaoTerapeuticaResponse])
def get_active_therapy(patient_id: int, db: Session = Depends(get_db)):
    _check_patient(db, patient_id)
    return db.query(models.MonitorizacaoTerapeutica).filter(
        models.MonitorizacaoTerapeutica.patient_id == patient_id,
        models.MonitorizacaoTerapeutica.status == "ativo",
    ).all()
