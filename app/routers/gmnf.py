from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter(tags=["gmnf"])


def _check_patient(db: Session, patient_id: int):
    if not db.query(models.Patient).filter(models.Patient.id == patient_id).first():
        raise HTTPException(status_code=404, detail="Paciente não encontrado")


@router.get("/api/patients/{patient_id}/gmnf", response_model=list[schemas.DecisaoGMNFResponse])
def list_gmnf(patient_id: int, db: Session = Depends(get_db)):
    _check_patient(db, patient_id)
    return db.query(models.DecisaoGMNF).filter(
        models.DecisaoGMNF.patient_id == patient_id
    ).order_by(models.DecisaoGMNF.data_reuniao.desc()).all()


@router.post("/api/patients/{patient_id}/gmnf", response_model=schemas.DecisaoGMNFResponse, status_code=201)
def create_gmnf(patient_id: int, data: schemas.DecisaoGMNFCreate, db: Session = Depends(get_db)):
    _check_patient(db, patient_id)
    decision = models.DecisaoGMNF(patient_id=patient_id, **data.model_dump())
    db.add(decision)
    db.commit()
    db.refresh(decision)
    return decision


@router.put("/api/gmnf/{gmnf_id}", response_model=schemas.DecisaoGMNFResponse)
def update_gmnf(gmnf_id: int, data: schemas.DecisaoGMNFUpdate, db: Session = Depends(get_db)):
    decision = db.query(models.DecisaoGMNF).filter(models.DecisaoGMNF.id == gmnf_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decisão GMNF não encontrada")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(decision, field, value)
    db.commit()
    db.refresh(decision)
    return decision


@router.get("/api/patients/{patient_id}/gmnf/{gmnf_id}", response_model=schemas.DecisaoGMNFResponse)
def get_gmnf(patient_id: int, gmnf_id: int, db: Session = Depends(get_db)):
    _check_patient(db, patient_id)
    decision = db.query(models.DecisaoGMNF).filter(
        models.DecisaoGMNF.id == gmnf_id,
        models.DecisaoGMNF.patient_id == patient_id,
    ).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decisão GMNF não encontrada")
    return decision
