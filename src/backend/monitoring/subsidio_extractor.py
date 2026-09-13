import os

from openai import OpenAI
from src.backend.monitoring.subsidio_schemas import (
    ComprovanteCreditoAnalysis,
    ContratoAnalysis,
    DemonstrativoDividaAnalysis,
    DossieAnalysis,
    ExtratoAnalysis,
    LaudoReferenciadoAnalysis,
)


class SubsidioExtractor:
    """Handles the extraction of domain-specific data from various legal supporting documents."""

    def __init__(self, api_key: str = None):
        """Initializes the OpenAI client with necessary configurations and timeouts."""
        self.client = OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            max_retries=2,
            timeout=20.0
        )

    def parse_document(self, doc_type: str, text: str):
        """Parses the text of a specific document type into its corresponding structured format."""
        if not text.strip():
            return None

        # Map document types to their respective extraction prompts and Pydantic schemas
        prompts_and_schemas = {
            "comprovante_credito": (
                "Você é um analista de operações. Extraia a data da liberação do crédito, valor depositado, banco e autenticação bancária.",
                ComprovanteCreditoAnalysis
            ),
            "contrato": (
                "Você é um especialista em contratos bancários. Extraia o número do contrato, valor total, taxa de juros e cláusulas críticas.",
                ContratoAnalysis
            ),
            "demonstrativo_divida": (
                "Você é um contador judicial. Extraia o valor principal, encargos, juros aplicados e o valor total atualizado da dívida.",
                DemonstrativoDividaAnalysis
            ),
            "dossie": (
                "Você é um analista de risco e prevenção a fraudes. Extraia o perfil do cliente, indícios de fraude e alertas internos.",
                DossieAnalysis
            ),
            "extrato": (
                "Você é um auditor financeiro. Extraia o período, saldos e movimentações financeiras relevantes do extrato.",
                ExtratoAnalysis
            ),
            "laudo_referenciado": (
                "Você é um perito judicial. Extraia a conclusão técnica do laudo e determine se o laudo é favorável à empresa.",
                LaudoReferenciadoAnalysis
            ),
        }

        if doc_type not in prompts_and_schemas:
            return None

        prompt, schema_class = prompts_and_schemas[doc_type]

        # Execute the parsed completion against the OpenAI API
        response = self.client.beta.chat.completions.parse(
            messages=[
                {"content": prompt, "role": "system"},
                {"content": f"Conteúdo do Documento ({doc_type}):\n{text}", "role": "user"}
            ],
            model="gpt-4o-mini",
            response_format=schema_class,
            temperature=0.0
        )

        return response.choices[0].message.parsed
