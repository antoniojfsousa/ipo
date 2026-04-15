from datetime import date, datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app import models


def _today_str() -> str:
    return date.today().isoformat()


def _days_since(date_str: str) -> int:
    """Return number of days since the given ISO date string."""
    try:
        d = date.fromisoformat(date_str)
        return (date.today() - d).days
    except (ValueError, TypeError):
        return 0


def _alert_exists(db: Session, patient_id: int, tipo_alerta: str) -> bool:
    """Check if an active alert of this type already exists for the patient."""
    return db.query(models.Alerta).filter(
        models.Alerta.patient_id == patient_id,
        models.Alerta.tipo_alerta == tipo_alerta,
        models.Alerta.status.in_(["ativo", "em_analise"]),
    ).first() is not None


def generate_alerts_for_patient(db: Session, patient_id: int) -> list:
    """Generate alerts for a single patient. Returns list of created alert objects."""
    created = []

    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        return created

    today = _today_str()

    # ── 1. Perda de seguimento (no consultation in last 12 months) ──
    last_consulta = (
        db.query(models.ConsultaClinica)
        .filter(models.ConsultaClinica.patient_id == patient_id)
        .order_by(models.ConsultaClinica.data_consulta.desc())
        .first()
    )
    if last_consulta is None or _days_since(last_consulta.data_consulta) > 365:
        if not _alert_exists(db, patient_id, "perda_seguimento"):
            alerta = models.Alerta(
                patient_id=patient_id,
                tipo_alerta="perda_seguimento",
                prioridade="alta",
                titulo=f"Doente sem consulta há mais de 12 meses",
                descricao=(
                    f"Último registo de consulta: {last_consulta.data_consulta if last_consulta else 'Nenhum'}"
                ),
                data_criacao=today,
                status="ativo",
            )
            db.add(alerta)
            db.flush()
            created.append(alerta)

    # ── 2. Exame solicitado não realizado (> 30 days) ──
    pending_exams = (
        db.query(models.Exame)
        .filter(
            models.Exame.patient_id == patient_id,
            models.Exame.status == "solicitado",
        )
        .all()
    )
    for exam in pending_exams:
        if _days_since(exam.data_solicitacao) > 30:
            tipo = "exame_solicitado_nao_realizado"
            # Check duplicate per exam reference
            dup = db.query(models.Alerta).filter(
                models.Alerta.patient_id == patient_id,
                models.Alerta.tipo_alerta == tipo,
                models.Alerta.referencia_id == exam.id,
                models.Alerta.status.in_(["ativo", "em_analise"]),
            ).first()
            if not dup:
                alerta = models.Alerta(
                    patient_id=patient_id,
                    tipo_alerta=tipo,
                    prioridade="media",
                    titulo=f"Exame {exam.tipo_exame} solicitado há mais de 30 dias sem realização",
                    descricao=f"Exame solicitado em {exam.data_solicitacao}. Subtipo: {exam.subtipo or 'N/A'}",
                    data_criacao=today,
                    status="ativo",
                    referencia_tipo="exame",
                    referencia_id=exam.id,
                )
                db.add(alerta)
                db.flush()
                created.append(alerta)

    # ── 3. Resultado crítico não alertado ──
    critical_exams = (
        db.query(models.Exame)
        .filter(
            models.Exame.patient_id == patient_id,
            models.Exame.resultado_critico == True,
            models.Exame.alerta_gerado == False,
        )
        .all()
    )
    for exam in critical_exams:
        alerta = models.Alerta(
            patient_id=patient_id,
            tipo_alerta="resultado_critico",
            prioridade="critica",
            titulo=f"Resultado crítico em exame {exam.tipo_exame}",
            descricao=f"Resultado crítico registado em {exam.data_resultado or exam.data_realizacao or 'data desconhecida'}. {exam.resultado_resumo or ''}",
            data_criacao=today,
            status="ativo",
            referencia_tipo="exame",
            referencia_id=exam.id,
        )
        db.add(alerta)
        exam.alerta_gerado = True
        db.flush()
        created.append(alerta)

    # ── 4. Exame periódico em atraso (RM last 12 months) ──
    last_rm = (
        db.query(models.Exame)
        .filter(
            models.Exame.patient_id == patient_id,
            models.Exame.tipo_exame == "RM",
            models.Exame.status.in_(["realizado", "resultado_disponivel"]),
        )
        .order_by(models.Exame.data_realizacao.desc())
        .first()
    )
    if last_rm is None or _days_since(last_rm.data_realizacao or last_rm.data_solicitacao) > 365:
        if not _alert_exists(db, patient_id, "exame_em_atraso"):
            alerta = models.Alerta(
                patient_id=patient_id,
                tipo_alerta="exame_em_atraso",
                prioridade="media",
                titulo="RM anual em atraso",
                descricao=(
                    f"Último RM realizado: {last_rm.data_realizacao if last_rm else 'Nenhum'}"
                ),
                data_criacao=today,
                status="ativo",
                referencia_tipo="exame",
            )
            db.add(alerta)
            db.flush()
            created.append(alerta)

    db.commit()
    return created


def run_all_alerts(db: Session) -> dict:
    """Run alert generation for every patient."""
    patients = db.query(models.Patient).all()
    total_created = 0
    for patient in patients:
        alerts = generate_alerts_for_patient(db, patient.id)
        total_created += len(alerts)
    return {"patients_checked": len(patients), "alerts_created": total_created}
