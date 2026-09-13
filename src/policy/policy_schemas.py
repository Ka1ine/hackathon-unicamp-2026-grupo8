from pydantic import BaseModel, Field

class PolicyDecision(BaseModel):
    """Structured output for the Settlement Policy Engine."""
    next_recommended_action: str = Field(..., description="Ação sugerida: Defesa, Acordo Estratégico ou Acordo Mandatório.")
    risk_level: str = Field(..., description="Nível de risco classificado pelo modelo (baixo, médio, alto).")
    estimated_operacional_cost: float = Field(..., description="Custo dinâmico calculado para manter a defesa.")
    proposed_value_initial: float = Field(..., description="Valor calculado para primeira oferta de acordo.")
    proposed_value_maximum: float = Field(..., description="Valor máximo aceitável para fechar o acordo.")
