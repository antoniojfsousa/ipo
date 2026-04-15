from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.services.nlp_service import parse_clinical_note
from datetime import date

router = APIRouter(tags=["consultas"])


def _check_patient(db: Session, patient_id: int):
    if not db.query(models.Patient).filter(models.Patient.id == patient_id).first():
        raise HTTPException(status_code=404, detail="Paciente não encontrado")


@router.get("/api/patients/{patient_id}/consultas", response_model=list[schemas.ConsultaClinicaResponse])
def list_consultas(patient_id: int, db: Session = Depends(get_db)):
    _check_patient(db, patient_id)
    return db.query(models.ConsultaClinica).filter(
        models.ConsultaClinica.patient_id == patient_id
    ).order_by(models.ConsultaClinica.data_consulta.desc()).all()


@router.post("/api/patients/{patient_id}/consultas", response_model=schemas.ConsultaClinicaResponse, status_code=201)
def create_consulta(patient_id: int, data: schemas.ConsultaClinicaCreate, db: Session = Depends(get_db)):
    _check_patient(db, patient_id)
    consulta = models.ConsultaClinica(patient_id=patient_id, **data.model_dump())
    db.add(consulta)
    db.commit()
    db.refresh(consulta)

    # NLP parsing of clinical notes
    if consulta.notas_clinicas:
        findings = parse_clinical_note(consulta.notas_clinicas)
        for sug in findings.get("suggestions", []):
            suggestion = models.SugestaoSistema(
                patient_id=patient_id,
                tipo=sug["tipo"],
                titulo=sug["titulo"],
                descricao=sug.get("descricao"),
                dados_sugeridos=sug.get("dados_sugeridos"),
                fonte=sug.get("fonte", "nlp"),
                status="pendente",
            )
            db.add(suggestion)
        db.commit()

    return consulta


@router.put("/api/consultas/{consulta_id}", response_model=schemas.ConsultaClinicaResponse)
def update_consulta(consulta_id: int, data: schemas.ConsultaClinicaUpdate, db: Session = Depends(get_db)):
    consulta = db.query(models.ConsultaClinica).filter(models.ConsultaClinica.id == consulta_id).first()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(consulta, field, value)
    db.commit()
    db.refresh(consulta)
    return consulta


@router.get("/api/consultas/{consulta_id}", response_model=schemas.ConsultaClinicaResponse)
def get_consulta(consulta_id: int, db: Session = Depends(get_db)):
    consulta = db.query(models.ConsultaClinica).filter(models.ConsultaClinica.id == consulta_id).first()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    return consulta
