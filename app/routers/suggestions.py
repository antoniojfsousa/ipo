from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter(tags=["suggestions"])


@router.get("/api/suggestions", response_model=list[schemas.SugestaoSistemaResponse])
def list_suggestions(status: str = "pendente", db: Session = Depends(get_db)):
    return db.query(models.SugestaoSistema).filter(
        models.SugestaoSistema.status == status
    ).order_by(models.SugestaoSistema.created_at.desc()).all()


@router.get("/api/patients/{patient_id}/suggestions", response_model=list[schemas.SugestaoSistemaResponse])
def list_patient_suggestions(patient_id: int, db: Session = Depends(get_db)):
    if not db.query(models.Patient).filter(models.Patient.id == patient_id).first():
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return db.query(models.SugestaoSistema).filter(
        models.SugestaoSistema.patient_id == patient_id
    ).order_by(models.SugestaoSistema.created_at.desc()).all()


@router.put("/api/suggestions/{suggestion_id}", response_model=schemas.SugestaoSistemaResponse)
def update_suggestion(suggestion_id: int, data: schemas.SugestaoSistemaUpdate, db: Session = Depends(get_db)):
    sug = db.query(models.SugestaoSistema).filter(models.SugestaoSistema.id == suggestion_id).first()
    if not sug:
        raise HTTPException(status_code=404, detail="Sugestão não encontrada")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(sug, field, value)
    db.commit()
    db.refresh(sug)
    return sug
