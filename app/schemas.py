from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator


# ──────────────────────────────────────────────
# Patient
# ──────────────────────────────────────────────

class PatientBase(BaseModel):
    numero_processo: str
    nome_completo: str
    data_nascimento: str
    genero: str
    nif: Optional[str] = None
    numero_sns: Optional[str] = None
    morada: Optional[str] = None
    codigo_postal: Optional[str] = None
    localidade: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    tutor_nome: Optional[str] = None
    tutor_relacao: Optional[str] = None
    tutor_contacto: Optional[str] = None
    nf1_confirmado: bool = False
    data_diagnostico: Optional[str] = None
    mutacao_genetica: Optional[str] = None
    medico_responsavel: Optional[str] = None
    enfermeiro_referencia: Optional[str] = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    nome_completo: Optional[str] = None
    data_nascimento: Optional[str] = None
    genero: Optional[str] = None
    nif: Optional[str] = None
    numero_sns: Optional[str] = None
    morada: Optional[str] = None
    codigo_postal: Optional[str] = None
    localidade: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    tutor_nome: Optional[str] = None
    tutor_relacao: Optional[str] = None
    tutor_contacto: Optional[str] = None
    nf1_confirmado: Optional[bool] = None
    data_diagnostico: Optional[str] = None
    mutacao_genetica: Optional[str] = None
    medico_responsavel: Optional[str] = None
    enfermeiro_referencia: Optional[str] = None


class PatientResponse(PatientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PatientSummary(BaseModel):
    id: int
    numero_processo: str
    nome_completo: str
    data_nascimento: str
    genero: str
    nf1_confirmado: bool
    medico_responsavel: Optional[str]
    has_active_consent: bool
    active_alerts_count: int
    last_consulta: Optional[str]

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# Informed Consent
# ──────────────────────────────────────────────

class InformedConsentBase(BaseModel):
    tipo_consentimento: str  # dados_clinicos/investigacao/ambos
    data_consentimento: str
    validade_ate: Optional[str] = None
    consentido_por: str  # patient/tutor
    nome_responsavel: str
    documento_assinado: Optional[str] = None
    ativo: bool = True
    observacoes: Optional[str] = None


class InformedConsentCreate(InformedConsentBase):
    pass


class InformedConsentUpdate(BaseModel):
    ativo: Optional[bool] = None
    validade_ate: Optional[str] = None
    observacoes: Optional[str] = None
    documento_assinado: Optional[str] = None


class InformedConsentResponse(InformedConsentBase):
    id: int
    patient_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# Consulta Clínica
# ──────────────────────────────────────────────

class ConsultaClinicaBase(BaseModel):
    data_consulta: str
    tipo_consulta: str  # rotina/urgencia/gmnf/seguimento
    medico: str
    especialidade: Optional[str] = None
    motivo: Optional[str] = None
    resumo_clinica: Optional[str] = None
    notas_clinicas: Optional[str] = None
    proxima_consulta: Optional[str] = None


class ConsultaClinicaCreate(ConsultaClinicaBase):
    pass


class ConsultaClinicaUpdate(BaseModel):
    data_consulta: Optional[str] = None
    tipo_consulta: Optional[str] = None
    medico: Optional[str] = None
    especialidade: Optional[str] = None
    motivo: Optional[str] = None
    resumo_clinica: Optional[str] = None
    notas_clinicas: Optional[str] = None
    proxima_consulta: Optional[str] = None


class ConsultaClinicaResponse(ConsultaClinicaBase):
    id: int
    patient_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# Decisão GMNF
# ──────────────────────────────────────────────

class DecisaoGMNFBase(BaseModel):
    data_reuniao: str
    numero_reuniao: Optional[str] = None
    indicacao_tratamento: Optional[str] = None
    tratamento_proposto: Optional[str] = None
    justificacao: Optional[str] = None
    decisao: str  # aprovado/recusado/pendente/aguarda_exames
    observacoes: Optional[str] = None
    medico_responsavel: Optional[str] = None


class DecisaoGMNFCreate(DecisaoGMNFBase):
    pass


class DecisaoGMNFUpdate(BaseModel):
    data_reuniao: Optional[str] = None
    numero_reuniao: Optional[str] = None
    indicacao_tratamento: Optional[str] = None
    tratamento_proposto: Optional[str] = None
    justificacao: Optional[str] = None
    decisao: Optional[str] = None
    observacoes: Optional[str] = None
    medico_responsavel: Optional[str] = None


class DecisaoGMNFResponse(DecisaoGMNFBase):
    id: int
    patient_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# Monitorização Terapêutica
# ──────────────────────────────────────────────

class MonitorizacaoTerapeuticaBase(BaseModel):
    farmaco: str
    data_inicio: str
    data_fim: Optional[str] = None
    dose_mg: Optional[float] = None
    frequencia: Optional[str] = None
    indicacao: Optional[str] = None
    numero_ciclo: Optional[int] = None
    status: str  # ativo/suspenso/terminado/aguarda_inicio
    eventos_adversos: Optional[str] = None
    avaliacao_resposta: Optional[str] = None
    medico_prescritor: Optional[str] = None
    observacoes: Optional[str] = None


class MonitorizacaoTerapeuticaCreate(MonitorizacaoTerapeuticaBase):
    pass


class MonitorizacaoTerapeuticaUpdate(BaseModel):
    farmaco: Optional[str] = None
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None
    dose_mg: Optional[float] = None
    frequencia: Optional[str] = None
    indicacao: Optional[str] = None
    numero_ciclo: Optional[int] = None
    status: Optional[str] = None
    eventos_adversos: Optional[str] = None
    avaliacao_resposta: Optional[str] = None
    medico_prescritor: Optional[str] = None
    observacoes: Optional[str] = None


class MonitorizacaoTerapeuticaResponse(MonitorizacaoTerapeuticaBase):
    id: int
    patient_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# Exame
# ──────────────────────────────────────────────

class ExameBase(BaseModel):
    tipo_exame: str
    subtipo: Optional[str] = None
    data_solicitacao: str
    data_realizacao: Optional[str] = None
    data_resultado: Optional[str] = None
    solicitado_por: Optional[str] = None
    local_realizacao: Optional[str] = None
    status: str  # solicitado/agendado/realizado/resultado_disponivel/cancelado
    resultado_resumo: Optional[str] = None
    resultado_critico: bool = False
    resultado_path: Optional[str] = None
    observacoes: Optional[str] = None


class ExameCreate(ExameBase):
    pass


class ExameUpdate(BaseModel):
    tipo_exame: Optional[str] = None
    subtipo: Optional[str] = None
    data_solicitacao: Optional[str] = None
    data_realizacao: Optional[str] = None
    data_resultado: Optional[str] = None
    solicitado_por: Optional[str] = None
    local_realizacao: Optional[str] = None
    status: Optional[str] = None
    resultado_resumo: Optional[str] = None
    resultado_critico: Optional[bool] = None
    resultado_path: Optional[str] = None
    alerta_gerado: Optional[bool] = None
    observacoes: Optional[str] = None


class ExameResponse(ExameBase):
    id: int
    patient_id: int
    alerta_gerado: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# Alerta
# ──────────────────────────────────────────────

class AlertaBase(BaseModel):
    tipo_alerta: str
    prioridade: str  # critica/alta/media/baixa
    titulo: str
    descricao: Optional[str] = None
    data_criacao: str
    referencia_tipo: Optional[str] = None
    referencia_id: Optional[int] = None


class AlertaCreate(AlertaBase):
    pass


class AlertaUpdate(BaseModel):
    status: Optional[str] = None  # ativo/em_analise/resolvido/ignorado
    resolvido_por: Optional[str] = None
    data_resolucao: Optional[str] = None
    notas_resolucao: Optional[str] = None
    prioridade: Optional[str] = None


class AlertaResponse(AlertaBase):
    id: int
    patient_id: int
    status: str
    resolvido_por: Optional[str]
    data_resolucao: Optional[str]
    notas_resolucao: Optional[str]
    created_at: datetime
    patient_nome: Optional[str] = None
    patient_processo: Optional[str] = None

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# Sugestão do Sistema
# ──────────────────────────────────────────────

class SugestaoSistemaBase(BaseModel):
    tipo: str
    titulo: str
    descricao: Optional[str] = None
    dados_sugeridos: Optional[str] = None  # JSON string
    fonte: str  # nlp/alerta/sistema


class SugestaoSistemaCreate(SugestaoSistemaBase):
    pass


class SugestaoSistemaUpdate(BaseModel):
    status: Optional[str] = None  # pendente/aprovado/rejeitado
    validado_por: Optional[str] = None
    data_validacao: Optional[str] = None
    observacoes_validacao: Optional[str] = None


class SugestaoSistemaResponse(SugestaoSistemaBase):
    id: int
    patient_id: int
    status: str
    validado_por: Optional[str]
    data_validacao: Optional[str]
    observacoes_validacao: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# Timeline item (generic)
# ──────────────────────────────────────────────

class TimelineItem(BaseModel):
    date: str
    tipo: str  # consulta/gmnf/exame/terapeutica
    titulo: str
    descricao: Optional[str] = None
    status: Optional[str] = None
    referencia_id: int
    extra: Optional[dict] = None


# ──────────────────────────────────────────────
# Dashboard summary
# ──────────────────────────────────────────────

class DashboardSummary(BaseModel):
    total_patients: int
    active_alerts: int
    critical_alerts: int
    high_alerts: int
    pending_suggestions: int
    patients_without_consent: int
    alerts_by_type: dict
