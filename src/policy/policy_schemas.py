from pydantic import BaseModel, Field


class PolicyDecision(BaseModel):
    """Structured output for the Settlement Policy Engine."""
    
    estimated_operacional_cost: float = Field(..., description="Custo dinâmico calculado para manter a defesa.")
    next_recommended_action: str = Field(..., description="Ação sugerida: Defesa, Acordo Estratégico ou Acordo Mandatório.")
    proposed_value_initial: float = Field(..., description="Valor calculado para primeira oferta de acordo.")
    proposed_value_maximum: float = Field(..., description="Valor máximo aceitável para fechar o acordo.")
    risk_level: str = Field(..., description="Nível de risco classificado pelo modelo (baixo, médio, alto).")