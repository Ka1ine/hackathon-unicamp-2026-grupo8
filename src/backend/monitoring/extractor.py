import os

from dotenv import load_dotenv
from openai import OpenAI
from src.backend.monitoring.schemas import CaseProgressionResponse

# Load environment variables
load_dotenv()

class CaseProgressionExtractor:
    """Handles the extraction of case timeline events and progression."""

    def __init__(self, api_key: str = None):
        """Initializes the OpenAI client with constraints."""
        self.client = OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            max_retries=2,
            timeout=20.0
        )

    def extract_progression(self, process_id: str, case_text: str) -> CaseProgressionResponse:
        """Parses raw case movements into a structured Pydantic response."""
        # Defines extraction rules for the LLM
        system_prompt = (
            "Você é um assistente jurídico especializado em análise de movimentações processuais brasileiras. "
            "Seu objetivo primário é mapear a linha do tempo do processo e identificar rigorosamente prazos (deadlines) "
            "e ações requeridas (action_required) pelo advogado.\n\n"
            "Regras de Extração:\n"
            "1. Para cada movimentação, avalie se há um prazo explícito (ex: 'prazo de 15 dias'). Se houver, deduza a data limite aproximada.\n"
            "2. Enquadre a ação necessária estritamente em uma das opções fornecidas. Se for apenas um despacho de mero expediente, classifique como 'Aguardar (Nenhuma ação imediata)'.\n"
            "3. O campo 'next_recommended_action' da resposta raiz deve refletir a ação urgente mais recente.\n"
        )

        # Sends the payload to OpenAI for structured parsing
        response = self.client.beta.chat.completions.parse(
            messages=[
                {"content": system_prompt, "role": "system"},
                {"content": f"ID: {process_id}\n\nMovimentações Extraídas:\n{case_text}", "role": "user"}
            ],
            model="gpt-4o-mini",
            response_format=CaseProgressionResponse,
            temperature=0.0  # Temperatura 0 para evitar alucinações em datas e prazos
        )

        return response.choices[0].message.parsed

class SubsidioExtractor:
    """Handles the extraction of supporting legal documents."""

    def __init__(self, api_key: str = None):
        """Initializes the OpenAI client with constraints."""
        # Enforce maximum timeout of 20 seconds per request
        self.client = OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            max_retries=2,
            timeout=20.0
        )
