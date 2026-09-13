from datetime import date
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional

class CommonAction(str, Enum):
    """Standardized required actions for case events."""
    AGUARDAR_DECISAO = "Aguardar (Nenhuma ação imediata)"
    COMPARECER_AUDIENCIA = "Comparecer à Audiência"
    OUTROS = "Outros"
    PAGAR_CUSTAS = "Pagar Custas/Multa/Condenação"
    PROTOCOLAR_PETICAO = "Protocolar Petição/Manifestação"
    PROTOCOLAR_RECURSO = "Protocolar Recurso"

class LegalStage(str, Enum):
    """Standardized legal stages of a case."""
    APPEAL = "Recurso"
    CITATION = "Citação"
    DEFENSE = "Contestação"
    EXECUTION = "Execução"
    HEARING = "Audiência"
    OTHER = "Outros"
    PETITION = "Petição Inicial"
    SENTENCE = "Sentença"

class TimelineEvent(BaseModel):
    """Represents a single event or movement in the case timeline."""
    action_required: CommonAction = Field(..., description="Ação padronizada necessária por parte do advogado.")
    date: Optional[str] = Field(None, description="Data do evento (YYYY-MM-DD).")
    deadline: Optional[str] = Field(None, description="Data limite para a ação (YYYY-MM-DD). Nulo se não houver prazo.")
    stage: LegalStage = Field(..., description="Fase processual identificada.")
    summary: str = Field(..., description="Resumo em 1-2 frases.")
    title: str = Field(..., description="Título resumido da movimentação.")
    source: Optional[str] = Field(None, description="Origem da informação: 'files' ou 'web'.")

class CaseProgressionResponse(BaseModel):
    """Consolidated response containing the case progression and timeline."""
    current_stage: LegalStage = Field(..., description="Fase atual do processo.")
    next_recommended_action: CommonAction = Field(..., description="Próximo passo consolidado para o advogado.")
    process_id: str = Field(..., description="Identificador único do processo.")
    risk_level: str = Field("Médio", description="Nível de risco/urgência: Baixo, Médio, Alto.")
    timeline: List[TimelineEvent] = Field(default_factory=list)
