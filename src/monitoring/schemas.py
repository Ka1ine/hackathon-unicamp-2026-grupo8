from datetime import date
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class LegalStage(str, Enum):
    PETITION = "Petição Inicial"
    CITATION = "Citação"
    DEFENSE = "Contestação"
    HEARING = "Audiência"
    SENTENCE = "Sentença"
    APPEAL = "Recurso"
    EXECUTION = "Execução"
    OTHER = "Outros"

class TimelineEvent(BaseModel):
    date: Optional[str] = Field(None, description="Data do evento no formato YYYY-MM-DD se identificada.")
    stage: LegalStage = Field(..., description="Fase processual identificada.")
    title: str = Field(..., description="Título resumido da movimentação.")
    summary: str = Field(..., description="Resumo em 1-2 frases da decisão ou documento.")
    action_required: bool = Field(False, description="Indica se exige ação imediata do advogado.")
    deadline: Optional[str] = Field(None, description="Data limite para resposta, se houver.")

class CaseProgressionResponse(BaseModel):
    process_id: str = Field(..., description="Identificador único do processo.")
    current_stage: LegalStage = Field(..., description="Fase atual do processo.")
    risk_level: str = Field("Médio", description="Nível de risco/urgência: Baixo, Médio, Alto.")
    next_recommended_action: str = Field(..., description="Próximo passo recomendado para o advogado.")
    timeline: List[TimelineEvent] = Field(default_factory=list, description="Lista cronológica dos eventos.")
