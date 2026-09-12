from typing import Optional, List
from pydantic import BaseModel, Field

class ContratoAnalysis(BaseModel):
    contrato_numero: Optional[str] = Field(None, description="Número do contrato.")
    valor_total: Optional[float] = Field(None, description="Valor total do contrato/empréstimo.")
    taxa_juros_mensal: Optional[str] = Field(None, description="Taxa de juros ao mês, se mencionada.")
    data_assinatura: Optional[str] = Field(None, description="Data da assinatura (YYYY-MM-DD).")
    clausulas_criticas: List[str] = Field(default_factory=list, description="Cláusulas de multa, atraso ou foro.")

class ExtratoAnalysis(BaseModel):
    periodo: Optional[str] = Field(None, description="Período coberto pelo extrato.")
    saldo_inicial: Optional[float] = Field(None, description="Saldo no início do período.")
    saldo_final: Optional[float] = Field(None, description="Saldo no fim do período.")
    transacoes_relevantes: List[str] = Field(default_factory=list, description="Lançamentos relevantes de débito/crédito.")

class ComprovanteCreditoAnalysis(BaseModel):
    data_deposito: Optional[str] = Field(None, description="Data do depósito/liberação do crédito.")
    valor_creditado: Optional[float] = Field(None, description="Valor efetivamente creditado.")
    banco_destino: Optional[str] = Field(None, description="Instituição bancária e conta de destino.")
    autenticacao_bancaria: Optional[str] = Field(None, description="Código de autenticação da transação.")

class DossieAnalysis(BaseModel):
    perfil_cliente: Optional[str] = Field(None, description="Resumo do perfil do cliente/autor.")
    historico_fraude_ou_risco: Optional[str] = Field(None, description="Apontamentos de fraude ou risco interno.")
    alertas_internos: List[str] = Field(default_factory=list, description="Alertas gerados pelos sistemas internos.")

class DemonstrativoDividaAnalysis(BaseModel):
    valor_principal: Optional[float] = Field(None, description="Valor original do débito.")
    encargos_e_juros: Optional[float] = Field(None, description="Soma de juros e correções aplicada.")
    valor_total_atualizado: Optional[float] = Field(None, description="Valor final calculado da dívida.")
    data_calculo: Optional[str] = Field(None, description="Data em que o cálculo foi realizado.")

class LaudoReferenciadoAnalysis(BaseModel):
    perito_responsavel: Optional[str] = Field(None, description="Nome ou órgão do perito autor do laudo.")
    conclusao_principal: Optional[str] = Field(None, description="Conclusão técnica do laudo.")
    favoravel_ao_banco: Optional[bool] = Field(None, description="Se a conclusão técnica é favorável à empresa.")
class ContratoDocument(BaseModel):
    file_name: str
    added_date: str
    extracted_info: Optional[ContratoAnalysis]

class ExtratoDocument(BaseModel):
    file_name: str
    added_date: str
    extracted_info: Optional[ExtratoAnalysis]

class ComprovanteCreditoDocument(BaseModel):
    file_name: str
    added_date: str
    extracted_info: Optional[ComprovanteCreditoAnalysis]

class DossieDocument(BaseModel):
    file_name: str
    added_date: str
    extracted_info: Optional[DossieAnalysis]

class DemonstrativoDividaDocument(BaseModel):
    file_name: str
    added_date: str
    extracted_info: Optional[DemonstrativoDividaAnalysis]

class LaudoReferenciadoDocument(BaseModel):
    file_name: str
    added_date: str
    extracted_info: Optional[LaudoReferenciadoAnalysis]

class CompleteSubsidioAnalysis(BaseModel):
    process_id: str
    contratos: List[ContratoDocument] = Field(default_factory=list)
    extratos: List[ExtratoDocument] = Field(default_factory=list)
    comprovantes_credito: List[ComprovanteCreditoDocument] = Field(default_factory=list)
    dossies: List[DossieDocument] = Field(default_factory=list)
    demonstrativos_divida: List[DemonstrativoDividaDocument] = Field(default_factory=list)
    laudos_referenciados: List[LaudoReferenciadoDocument] = Field(default_factory=list)