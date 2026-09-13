from pathlib import Path

import pytest
from dotenv import load_dotenv

from src.backend.monitoring.service import MonitoringService
from src.backend.monitoring.subsidio_service import SubsidioService

# Ensure environment variables (like OPENAI_API_KEY) are loaded for the tests
load_dotenv()


# -----------------------------------------------------------------------------
# Fixtures (Alphabetical Order)
# -----------------------------------------------------------------------------

@pytest.fixture
def mock_html_file(tmp_path):
    """Creates a mock HTML file in a temporary directory for scraping tests."""
    html_file = tmp_path / "sample_case.html"
    mock_html_content = (
        "<html><body>"
        "<div>Movimentação 1: Intimação expedida. Prazo de 15 dias para manifestação.</div>"
        "</body></html>"
    )
    html_file.write_text(mock_html_content, encoding="utf-8")
    
    return str(html_file)


@pytest.fixture
def mock_subsidios_env(tmp_path):
    """Sets up a temporary directory structure populated with fake legal documents."""
    base_dir = tmp_path / "subsidios"
    cache_dir = tmp_path / "cache"
    process_id = "test_subsidios"
    process_dir = base_dir / process_id
    
    # Create the necessary folder structure
    process_dir.mkdir(exist_ok=True, parents=True)
    
    # Write mock document files for extraction testing
    (process_dir / "contrato_aditivo.txt").write_text(
        "Aditivo ao Contrato nº 111. Novo valor total: R$ 50.000,00. Taxa: 1.8% ao mês. Assinado em 2024-05-10."
    )
    (process_dir / "contrato_original.txt").write_text(
        "Contrato nº 111. Valor total: R$ 40.000,00. Taxa de juros: 1.5% ao mês. Assinado em 2023-01-10."
    )
    (process_dir / "demonstrativo_divida_v1.txt").write_text(
        "Demonstrativo de Dívida. Valor Principal: R$ 50.000,00. Total Atualizado: R$ 52.000,00 em 2026-01-15."
    )
    
    return base_dir, cache_dir, process_id


# -----------------------------------------------------------------------------
# Tests (Alphabetical Order)
# -----------------------------------------------------------------------------

def test_monitoring_service(mock_html_file, tmp_path):
    """Validates the scraping, extraction, and timeline generation for a case."""
    process_id = "test_scrape"
    service = MonitoringService(cache_dir=tmp_path)
    
    # Execute the service logic against the mock HTML file
    result = service.get_or_update_case(process_id, mock_html_file, force_refresh=True)
    
    # Validate the resulting object and its schema
    assert result is not None, "O resultado não deveria ser nulo."
    assert result.process_id == process_id, "O ID do processo extraído deve corresponder ao solicitado."
    assert len(result.timeline) > 0, "Deveria haver pelo menos um evento extraído na timeline."


def test_subsidio_service(mock_subsidios_env):
    """Validates the bulk processing and extraction of legal supporting documents."""
    base_dir, cache_dir, process_id = mock_subsidios_env
    service = SubsidioService(base_data_dir=base_dir, cache_dir=cache_dir)
    
    # Execute the analysis workflow
    result = service.analyze_process_subsidios(process_id, force_refresh=True)
    
    # Validate the data aggregation and schema mapping
    assert result is not None, "O resultado da análise não deve ser nulo."
    assert len(result.contratos) == 2, "O sistema deveria ter identificado e extraído exatamente 2 contratos."
    assert len(result.demonstrativos_divida) == 1, "O sistema deveria ter identificado 1 demonstrativo de dívida."
    assert result.process_id == process_id, "O ID do processo no pacote final deve corresponder ao solicitado."
