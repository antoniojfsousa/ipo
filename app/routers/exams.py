from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter(tags=["exams"])


def _check_patient(db: Session, patient_id: int):
    if not db.query(models.Patient).filter(models.Patient.id == patient_id).first():
        raise HTTPException(status_code=404, detail="Paciente não encontrado")


@router.get("/api/patients/{patient_id}/exams", response_model=list[schemas.ExameResponse])
def list_exams(
    patient_id: int,
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    _check_patient(db, patient_id)
    query = db.query(models.Exame).filter(models.Exame.patient_id == patient_id)
    if status:
        query = query.filter(models.Exame.status == status)
    return query.order_by(models.Exame.data_solicitacao.desc()).all()


@router.post("/api/patients/{patient_id}/exams", response_model=schemas.ExameResponse, status_code=201)
def create_exam(patient_id: int, data: schemas.ExameCreate, db: Session = Depends(get_db)):
    _check_patient(db, patient_id)
    exam = models.Exame(patient_id=patient_id, **data.model_dump())
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam


@router.put("/api/exams/{exam_id}", response_model=schemas.ExameResponse)
def update_exam(exam_id: int, data: schemas.ExameUpdate, db: Session = Depends(get_db)):
    exam = db.query(models.Exame).filter(models.Exame.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exame não encontrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(exam, field, value)
    db.commit()
    db.refresh(exam)
    return exam


@router.get("/api/patients/{patient_id}/exams/pending", response_model=list[schemas.ExameResponse])
def get_pending_exams(patient_id: int, db: Session = Depends(get_db)):
    _check_patient(db, patient_id)
    return db.query(models.Exame).filter(
        models.Exame.patient_id == patient_id,
        models.Exame.status.in_(["solicitado", "agendado"]),
    ).order_by(models.Exame.data_solicitacao.desc()).all()
