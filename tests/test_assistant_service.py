import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.monitoring.assistant_service import ProcessAssistantService


def test_build_context_uses_only_the_requested_case():
    service = ProcessAssistantService()

    context, sources = service.build_context("0801234-56.2024.8.10.0001")

    assert "01_Autos_Processo_0801234-56-2024-8-10-0001.pdf" in sources
    assert "01_Autos_Processo_0654321-09-2024-8-04-0001.pdf" not in sources
    assert "JSON de monitoramento: _0801234-56-2024-8-10-0001.json" in sources
    assert "Propositura da Ação" in context


def test_build_context_rejects_invalid_process_id():
    service = ProcessAssistantService()

    try:
        service.build_context("../../dados")
    except ValueError:
        pass
    else:
        raise AssertionError("O identificador inválido deveria ser rejeitado.")
