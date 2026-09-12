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

class CommonAction(str, Enum):
    PROTOCOLAR_PETICAO = "Protocolar Petição/Manifestação"
    PROTOCOLAR_RECURSO = "Protocolar Recurso"
    COMPARECER_AUDIENCIA = "Comparecer à Audiência"
    PAGAR_CUSTAS = "Pagar Custas/Multa/Condenação"
    AGUARDAR_DECISAO = "Aguardar (Nenhuma ação imediata)"
    OUTROS = "Outros"

class TimelineEvent(BaseModel):
    date: Optional[str] = Field(None, description="Data do evento (YYYY-MM-DD).")
    stage: LegalStage = Field(..., description="Fase processual identificada.")
    title: str = Field(..., description="Título resumido da movimentação.")
    summary: str = Field(..., description="Resumo em 1-2 frases.")
    action_required: CommonAction = Field(..., description="Ação padronizada necessária por parte do advogado.")
    deadline: Optional[str] = Field(None, description="Data limite para a ação (YYYY-MM-DD). Nulo se não houver prazo.")

class CaseProgressionResponse(BaseModel):
    process_id: str = Field(..., description="Identificador único do processo.")
    current_stage: LegalStage = Field(..., description="Fase atual do processo.")
    risk_level: str = Field("Médio", description="Nível de risco/urgência: Baixo, Médio, Alto.")
    next_recommended_action: CommonAction = Field(..., description="Próximo passo consolidado para o advogado.")
    timeline: List[TimelineEvent] = Field(default_factory=list)