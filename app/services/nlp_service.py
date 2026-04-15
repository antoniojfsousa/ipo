import re
from typing import Optional


MEDICATION_KEYWORDS = [
    "selumetinib", "trametinib", "binimetinib", "cobimetinib", "refametinib",
    "mek inhibitor", "inibidor mek",
]

CRITICAL_KEYWORDS = [
    "tumor", "tumoral", "tumoração", "metástase", "metastase", "progressão",
    "progressao", "urgente", "urgência", "emergência", "emergencia",
    "transformação maligna", "transformacao maligna", "crescimento rápido",
    "crescimento rapido", "compressão medular", "compressao medular",
    "plexiforme sintomático", "plexiforme sintomatico", "défice neurológico",
    "defice neurologico",
]

EXAM_KEYWORDS = {
    "RM": ["ressonância magnética", "ressonancia magnetica", "rm crânio", "rm cranio",
           "rm cerebral", "rm coluna", "rm total", "rmn", "mri"],
    "TC": ["tomografia computorizada", "tc torácico", "tc toracico", "tc abdominal",
           "tc crânio", "tc cranio", "tac"],
    "PET": ["pet-ct", "pet ct", "pet scan", "tomografia por emissão"],
    "ecografia": ["ecografia", "eco abdominal", "ecografia abdominal", "ultrassom"],
    "analises": ["análises", "analises", "hemograma", "bioquímica", "bioquimica",
                 "ionograma", "função renal", "funcao renal", "função hepática"],
    "biopsia": ["biópsia", "biopsia"],
}


def parse_clinical_note(text: str) -> dict:
    """
    Keyword-based NLP parser for clinical notes.
    Returns a dict with findings and suggested SugestaoSistema entries.
    """
    if not text:
        return {"medications": [], "critical_findings": [], "suggested_exams": [], "suggestions": []}

    lower = text.lower()
    findings: dict = {
        "medications": [],
        "critical_findings": [],
        "suggested_exams": [],
        "suggestions": [],
    }

    # Medications
    for med in MEDICATION_KEYWORDS:
        if med in lower:
            if med not in findings["medications"]:
                findings["medications"].append(med)

    # Critical keywords
    for kw in CRITICAL_KEYWORDS:
        if kw in lower:
            if kw not in findings["critical_findings"]:
                findings["critical_findings"].append(kw)

    # Suggested exams
    for exam_type, keywords in EXAM_KEYWORDS.items():
        for kw in keywords:
            if kw in lower:
                if exam_type not in findings["suggested_exams"]:
                    findings["suggested_exams"].append(exam_type)
                break

    # Build suggestions
    if findings["medications"]:
        findings["suggestions"].append({
            "tipo": "atualizacao_dados",
            "titulo": "Medicação identificada nas notas clínicas",
            "descricao": f"Foram identificados os seguintes fármacos: {', '.join(findings['medications'])}",
            "dados_sugeridos": str({"farmaco": findings["medications"][0]}),
            "fonte": "nlp",
        })

    if findings["critical_findings"]:
        findings["suggestions"].append({
            "tipo": "alerta_nlp",
            "titulo": "Palavras-chave críticas identificadas",
            "descricao": f"Termos de alerta encontrados: {', '.join(findings['critical_findings'])}",
            "dados_sugeridos": str({"keywords": findings["critical_findings"]}),
            "fonte": "nlp",
        })

    if findings["suggested_exams"]:
        for exam in findings["suggested_exams"]:
            findings["suggestions"].append({
                "tipo": "novo_exame",
                "titulo": f"Possível solicitação de exame: {exam}",
                "descricao": f"Exame do tipo '{exam}' mencionado nas notas clínicas.",
                "dados_sugeridos": str({"tipo_exame": exam}),
                "fonte": "nlp",
            })

    return findings
