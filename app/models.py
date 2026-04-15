from datetime import datetime, timezone
from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float
)
from sqlalchemy.orm import relationship
from app.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    numero_processo = Column(String(50), unique=True, index=True, nullable=False)
    nome_completo = Column(String(200), nullable=False)
    data_nascimento = Column(String(10), nullable=False)  # ISO date string YYYY-MM-DD
    genero = Column(String(10), nullable=False)  # M / F / Outro

    nif = Column(String(20), nullable=True)
    numero_sns = Column(String(20), nullable=True)

    morada = Column(String(300), nullable=True)
    codigo_postal = Column(String(10), nullable=True)
    localidade = Column(String(100), nullable=True)
    telefone = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True)

    # Guardian (for minors)
    tutor_nome = Column(String(200), nullable=True)
    tutor_relacao = Column(String(100), nullable=True)
    tutor_contacto = Column(String(50), nullable=True)

    # Clinical
    nf1_confirmado = Column(Boolean, default=False)
    data_diagnostico = Column(String(10), nullable=True)
    mutacao_genetica = Column(String(200), nullable=True)

    medico_responsavel = Column(String(200), nullable=True)
    enfermeiro_referencia = Column(String(200), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    consents = relationship("InformedConsent", back_populates="patient", cascade="all, delete-orphan")
    consultas = relationship("ConsultaClinica", back_populates="patient", cascade="all, delete-orphan")
    gmnf_decisions = relationship("DecisaoGMNF", back_populates="patient", cascade="all, delete-orphan")
    therapy_records = relationship("MonitorizacaoTerapeutica", back_populates="patient", cascade="all, delete-orphan")
    exams = relationship("Exame", back_populates="patient", cascade="all, delete-orphan")
    alerts = relationship("Alerta", back_populates="patient", cascade="all, delete-orphan")
    suggestions = relationship("SugestaoSistema", back_populates="patient", cascade="all, delete-orphan")


class InformedConsent(Base):
    __tablename__ = "informed_consents"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    tipo_consentimento = Column(String(50), nullable=False)  # dados_clinicos/investigacao/ambos
    data_consentimento = Column(String(10), nullable=False)
    validade_ate = Column(String(10), nullable=True)
    consentido_por = Column(String(20), nullable=False)  # patient/tutor
    nome_responsavel = Column(String(200), nullable=False)
    documento_assinado = Column(String(500), nullable=True)
    ativo = Column(Boolean, default=True)
    observacoes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    patient = relationship("Patient", back_populates="consents")


class ConsultaClinica(Base):
    __tablename__ = "consultas_clinicas"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    data_consulta = Column(String(10), nullable=False)
    tipo_consulta = Column(String(30), nullable=False)  # rotina/urgencia/gmnf/seguimento
    medico = Column(String(200), nullable=False)
    especialidade = Column(String(100), nullable=True)
    motivo = Column(Text, nullable=True)
    resumo_clinica = Column(Text, nullable=True)
    notas_clinicas = Column(Text, nullable=True)
    proxima_consulta = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    patient = relationship("Patient", back_populates="consultas")


class DecisaoGMNF(Base):
    __tablename__ = "decisoes_gmnf"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    data_reuniao = Column(String(10), nullable=False)
    numero_reuniao = Column(String(50), nullable=True)
    indicacao_tratamento = Column(Text, nullable=True)
    tratamento_proposto = Column(Text, nullable=True)
    justificacao = Column(Text, nullable=True)
    decisao = Column(String(30), nullable=False)  # aprovado/recusado/pendente/aguarda_exames
    observacoes = Column(Text, nullable=True)
    medico_responsavel = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    patient = relationship("Patient", back_populates="gmnf_decisions")


class MonitorizacaoTerapeutica(Base):
    __tablename__ = "monitorizacao_terapeutica"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    farmaco = Column(String(50), nullable=False)  # selumetinib/trametinib/binimetinib/outro
    data_inicio = Column(String(10), nullable=False)
    data_fim = Column(String(10), nullable=True)
    dose_mg = Column(Float, nullable=True)
    frequencia = Column(String(100), nullable=True)
    indicacao = Column(Text, nullable=True)
    numero_ciclo = Column(Integer, nullable=True)
    status = Column(String(30), nullable=False)  # ativo/suspenso/terminado/aguarda_inicio
    eventos_adversos = Column(Text, nullable=True)
    avaliacao_resposta = Column(String(50), nullable=True)
    medico_prescritor = Column(String(200), nullable=True)
    observacoes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    patient = relationship("Patient", back_populates="therapy_records")


class Exame(Base):
    __tablename__ = "exames"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    tipo_exame = Column(String(50), nullable=False)  # RM/TC/PET/ecografia/analises/biopsia/outro
    subtipo = Column(String(100), nullable=True)
    data_solicitacao = Column(String(10), nullable=False)
    data_realizacao = Column(String(10), nullable=True)
    data_resultado = Column(String(10), nullable=True)
    solicitado_por = Column(String(200), nullable=True)
    local_realizacao = Column(String(200), nullable=True)
    status = Column(String(50), nullable=False)  # solicitado/agendado/realizado/resultado_disponivel/cancelado
    resultado_resumo = Column(Text, nullable=True)
    resultado_critico = Column(Boolean, default=False)
    resultado_path = Column(String(500), nullable=True)
    alerta_gerado = Column(Boolean, default=False)
    observacoes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    patient = relationship("Patient", back_populates="exams")


class Alerta(Base):
    __tablename__ = "alertas"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    tipo_alerta = Column(String(60), nullable=False)
    prioridade = Column(String(20), nullable=False)  # critica/alta/media/baixa
    titulo = Column(String(300), nullable=False)
    descricao = Column(Text, nullable=True)
    data_criacao = Column(String(10), nullable=False)
    status = Column(String(20), nullable=False, default="ativo")  # ativo/em_analise/resolvido/ignorado
    resolvido_por = Column(String(200), nullable=True)
    data_resolucao = Column(String(10), nullable=True)
    notas_resolucao = Column(Text, nullable=True)
    referencia_tipo = Column(String(50), nullable=True)  # consulta/exame/terapeutica/gmnf
    referencia_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    patient = relationship("Patient", back_populates="alerts")


class SugestaoSistema(Base):
    __tablename__ = "sugestoes_sistema"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    tipo = Column(String(50), nullable=False)  # atualizacao_dados/novo_exame/alerta_nlp/outro
    titulo = Column(String(300), nullable=False)
    descricao = Column(Text, nullable=True)
    dados_sugeridos = Column(Text, nullable=True)  # JSON text
    fonte = Column(String(20), nullable=False)  # nlp/alerta/sistema
    status = Column(String(20), nullable=False, default="pendente")  # pendente/aprovado/rejeitado
    validado_por = Column(String(200), nullable=True)
    data_validacao = Column(String(10), nullable=True)
    observacoes_validacao = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    patient = relationship("Patient", back_populates="suggestions")
