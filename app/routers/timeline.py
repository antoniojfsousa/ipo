from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter(tags=["timeline"])


@router.get("/api/patients/{patient_id}/timeline", response_model=list[schemas.TimelineItem])
def get_timeline(patient_id: int, db: Session = Depends(get_db)):
    if not db.query(models.Patient).filter(models.Patient.id == patient_id).first():
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    items: list[schemas.TimelineItem] = []

    # Consultas
    for c in db.query(models.ConsultaClinica).filter(
        models.ConsultaClinica.patient_id == patient_id
    ).all():
        items.append(schemas.TimelineItem(
            date=c.data_consulta,
            tipo="consulta",
            titulo=f"Consulta {c.tipo_consulta.capitalize()} — {c.medico}",
            descricao=c.resumo_clinica or c.motivo,
            status=c.tipo_consulta,
            referencia_id=c.id,
            extra={"especialidade": c.especialidade, "proxima_consulta": c.proxima_consulta},
        ))

    # GMNF
    for g in db.query(models.DecisaoGMNF).filter(
        models.DecisaoGMNF.patient_id == patient_id
    ).all():
        items.append(schemas.TimelineItem(
            date=g.data_reuniao,
            tipo="gmnf",
            titulo=f"Reunião GMNF {g.numero_reuniao or ''} — {g.decisao.capitalize()}",
            descricao=g.tratamento_proposto or g.justificacao,
            status=g.decisao,
            referencia_id=g.id,
            extra={"medico_responsavel": g.medico_responsavel},
        ))

    # Exames
    for e in db.query(models.Exame).filter(
        models.Exame.patient_id == patient_id
    ).all():
        date_to_use = e.data_realizacao or e.data_solicitacao
        items.append(schemas.TimelineItem(
            date=date_to_use,
            tipo="exame",
            titulo=f"Exame {e.tipo_exame}" + (f" — {e.subtipo}" if e.subtipo else ""),
            descricao=e.resultado_resumo or e.observacoes,
            status=e.status,
            referencia_id=e.id,
            extra={
                "resultado_critico": e.resultado_critico,
                "solicitado_por": e.solicitado_por,
                "data_solicitacao": e.data_solicitacao,
            },
        ))

    # Terapêutica
    for t in db.query(models.MonitorizacaoTerapeutica).filter(
        models.MonitorizacaoTerapeutica.patient_id == patient_id
    ).all():
        items.append(schemas.TimelineItem(
            date=t.data_inicio,
            tipo="terapeutica",
            titulo=f"Terapêutica: {t.farmaco.capitalize()}",
            descricao=t.indicacao,
            status=t.status,
            referencia_id=t.id,
            extra={
                "dose_mg": t.dose_mg,
                "frequencia": t.frequencia,
                "avaliacao_resposta": t.avaliacao_resposta,
            },
        ))

    items.sort(key=lambda x: x.date, reverse=True)
    return items
