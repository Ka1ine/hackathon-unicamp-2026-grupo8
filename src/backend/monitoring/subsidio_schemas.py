from pydantic import BaseModel, Field
from typing import List, Optional

class ComprovanteCreditoAnalysis(BaseModel):
    """Extraction schema for credit receipt documents."""
    autenticacao_bancaria: Optional[str] = Field(None, description="Código de autenticação da transação.")
    banco_destino: Optional[str] = Field(None, description="Instituição bancária e conta de destino.")
    data_deposito: Optional[str] = Field(None, description="Data do depósito/liberação do crédito.")
    valor_creditado: Optional[float] = Field(None, description="Valor efetivamente creditado.")

class ContratoAnalysis(BaseModel):
    """Extraction schema for banking contract documents."""
    clausulas_criticas: List[str] = Field(default_factory=list, description="Cláusulas de multa, atraso ou foro.")
    contrato_numero: Optional[str] = Field(None, description="Número do contrato.")
    data_assinatura: Optional[str] = Field(None, description="Data da assinatura (YYYY-MM-DD).")
    taxa_juros_mensal: Optional[str] = Field(None, description="Taxa de juros ao mês, se mencionada.")
    valor_total: Optional[float] = Field(None, description="Valor total do contrato/empréstimo.")

class DemonstrativoDividaAnalysis(BaseModel):
    """Extraction schema for debt statement documents."""
    data_calculo: Optional[str] = Field(None, description="Data em que o cálculo foi realizado.")
    encargos_e_juros: Optional[float] = Field(None, description="Soma de juros e correções aplicada.")
    valor_principal: Optional[float] = Field(None, description="Valor original do débito.")
    valor_total_atualizado: Optional[float] = Field(None, description="Valor final calculado da dívida.")

class DossieAnalysis(BaseModel):
    """Extraction schema for client dossier and risk documents."""
    alertas_internos: List[str] = Field(default_factory=list, description="Alertas gerados pelos sistemas internos.")
    historico_fraude_ou_risco: Optional[str] = Field(None, description="Apontamentos de fraude ou risco interno.")
    perfil_cliente: Optional[str] = Field(None, description="Resumo do perfil do cliente/autor.")

class ExtratoAnalysis(BaseModel):
    """Extraction schema for financial bank statements."""
    periodo: Optional[str] = Field(None, description="Período coberto pelo extrato.")
    saldo_final: Optional[float] = Field(None, description="Saldo no fim do período.")
    saldo_inicial: Optional[float] = Field(None, description="Saldo no início do período.")
    transacoes_relevantes: List[str] = Field(default_factory=list, description="Lançamentos relevantes de débito/crédito.")

class LaudoReferenciadoAnalysis(BaseModel):
    """Extraction schema for technical expert reports."""
    conclusao_principal: Optional[str] = Field(None, description="Conclusão técnica do laudo.")
    favoravel_ao_banco: Optional[bool] = Field(None, description="Se a conclusão técnica é favorável à empresa.")
    perito_responsavel: Optional[str] = Field(None, description="Nome ou órgão do perito autor do laudo.")

class ComprovanteCreditoDocument(BaseModel):
    """Wrapper for credit receipt documents including metadata."""
    added_date: str
    extracted_info: Optional[ComprovanteCreditoAnalysis]
    file_name: str

class ContratoDocument(BaseModel):
    """Wrapper for banking contract documents including metadata."""
    added_date: str
    extracted_info: Optional[ContratoAnalysis]
    file_name: str

class DemonstrativoDividaDocument(BaseModel):
    """Wrapper for debt statement documents including metadata."""
    added_date: str
    extracted_info: Optional[DemonstrativoDividaAnalysis]
    file_name: str

class DossieDocument(BaseModel):
    """Wrapper for dossier documents including metadata."""
    added_date: str
    extracted_info: Optional[DossieAnalysis]
    file_name: str

class ExtratoDocument(BaseModel):
    """Wrapper for financial statement documents including metadata."""
    added_date: str
    extracted_info: Optional[ExtratoAnalysis]
    file_name: str

class LaudoReferenciadoDocument(BaseModel):
    """Wrapper for expert report documents including metadata."""
    added_date: str
    extracted_info: Optional[LaudoReferenciadoAnalysis]
    file_name: str

class CompleteSubsidioAnalysis(BaseModel):
    """Comprehensive container for all processed supporting documents."""
    comprovantes_credito: List[ComprovanteCreditoDocument] = Field(default_factory=list)
    contratos: List[ContratoDocument] = Field(default_factory=list)
    demonstrativos_divida: List[DemonstrativoDividaDocument] = Field(default_factory=list)
    dossies: List[DossieDocument] = Field(default_factory=list)
    extratos: List[ExtratoDocument] = Field(default_factory=list)
    laudos_referenciados: List[LaudoReferenciadoDocument] = Field(default_factory=list)
    process_id: str
