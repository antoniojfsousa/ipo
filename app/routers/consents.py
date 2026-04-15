from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter(tags=["consents"])


@router.get("/api/patients/{patient_id}/consents", response_model=list[schemas.InformedConsentResponse])
def list_consents(patient_id: int, db: Session = Depends(get_db)):
    _check_patient(db, patient_id)
    return db.query(models.InformedConsent).filter(
        models.InformedConsent.patient_id == patient_id
    ).order_by(models.InformedConsent.data_consentimento.desc()).all()


@router.post("/api/patients/{patient_id}/consents", response_model=schemas.InformedConsentResponse, status_code=201)
def create_consent(patient_id: int, data: schemas.InformedConsentCreate, db: Session = Depends(get_db)):
    _check_patient(db, patient_id)
    consent = models.InformedConsent(patient_id=patient_id, **data.model_dump())
    db.add(consent)
    db.commit()
    db.refresh(consent)
    return consent


@router.put("/api/consents/{consent_id}", response_model=schemas.InformedConsentResponse)
def update_consent(consent_id: int, data: schemas.InformedConsentUpdate, db: Session = Depends(get_db)):
    consent = db.query(models.InformedConsent).filter(models.InformedConsent.id == consent_id).first()
    if not consent:
        raise HTTPException(status_code=404, detail="Consentimento não encontrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(consent, field, value)
    db.commit()
    db.refresh(consent)
    return consent


@router.get("/api/patients/{patient_id}/consents/current", response_model=schemas.InformedConsentResponse)
def get_current_consent(patient_id: int, db: Session = Depends(get_db)):
    _check_patient(db, patient_id)
    consent = db.query(models.InformedConsent).filter(
        models.InformedConsent.patient_id == patient_id,
        models.InformedConsent.ativo == True,
    ).order_by(models.InformedConsent.data_consentimento.desc()).first()
    if not consent:
        raise HTTPException(status_code=404, detail="Nenhum consentimento ativo")
    return consent


def _check_patient(db: Session, patient_id: int):
    if not db.query(models.Patient).filter(models.Patient.id == patient_id).first():
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
