import os
from openai import OpenAI
from src.monitoring.subsidio_schemas import (
    ContratoAnalysis, ExtratoAnalysis, ComprovanteCreditoAnalysis,
    DossieAnalysis, DemonstrativoDividaAnalysis, LaudoReferenciadoAnalysis
)

class SubsidioExtractor:
    def __init__(self, api_key: str = None):
        self.client = OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            timeout=20.0,
            max_retries=2
        )

    def parse_document(self, doc_type: str, text: str):
        if not text.strip():
            return None

        prompts_and_schemas = {
            "contrato": (
                "Você é um especialista em contratos bancários. Extraia o número do contrato, valor total, taxa de juros e cláusulas críticas.",
                ContratoAnalysis
            ),
            "extrato": (
                "Você é um auditor financeiro. Extraia o período, saldos e movimentações financeiras relevantes do extrato.",
                ExtratoAnalysis
            ),
            "comprovante_credito": (
                "Você é um analista de operações. Extraia a data da liberação do crédito, valor depositado, banco e autenticação bancária.",
                ComprovanteCreditoAnalysis
            ),
            "dossie": (
                "Você é um analista de risco e prevenção a fraudes. Extraia o perfil do cliente, indícios de fraude e alertas internos.",
                DossieAnalysis
            ),
            "demonstrativo_divida": (
                "Você é um contador judicial. Extraia o valor principal, encargos, juros aplicados e o valor total atualizado da dívida.",
                DemonstrativoDividaAnalysis
            ),
            "laudo_referenciado": (
                "Você é um perito judicial. Extraia a conclusão técnica do laudo e determine se o laudo é favorável à empresa.",
                LaudoReferenciadoAnalysis
            ),
        }

        if doc_type not in prompts_and_schemas:
            return None

        prompt, schema_class = prompts_and_schemas[doc_type]

        response = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Conteúdo do Documento ({doc_type}):\n{text}"}
            ],
            response_format=schema_class,
            temperature=0.0
        )

        return response.choices[0].message.parsed
