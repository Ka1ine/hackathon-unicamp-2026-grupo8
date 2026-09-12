import os
from dotenv import load_dotenv
from openai import OpenAI
from src.monitoring.schemas import CaseProgressionResponse

load_dotenv()

class CaseProgressionExtractor:
    def __init__(self, api_key: str = None):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def extract_progression(self, process_id: str, case_text: str) -> CaseProgressionResponse:
        system_prompt = (
            "Você é um assistente jurídico especializado em análise processual civil brasileira. "
            "Examine o texto fornecido dos autos do processo e extraia a cronologia das fases, "
            "identifique a fase atual, riscos e recomendações de ações necessárias."
        )

        response = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"ID do Processo: {process_id}\n\nConteúdo dos Autos:\n{case_text}"}
            ],
            response_format=CaseProgressionResponse,
            temperature=0.1
        )

        return response.choices[0].message.parsed
