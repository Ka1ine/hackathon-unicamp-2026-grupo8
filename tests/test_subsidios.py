from dotenv import load_dotenv
from pathlib import Path

from src.monitoring.subsidio_service import SubsidioService

# Load environment variables to ensure API keys are available
load_dotenv()

def run_test():
    """Generates mock legal documents and validates the subsidio extraction service."""
    # Define test parameters and paths
    case_id = "test_subsidios"
    mock_dir = Path("data/subsidios") / case_id
    
    # Ensure the target directory structure exists
    mock_dir.mkdir(exist_ok=True, parents=True)
    
    # Create multiple mock files of the same and different types to test list aggregation
    (mock_dir / "contrato_aditivo.txt").write_text(
        "Aditivo ao Contrato nº 111. Novo valor total: R$ 50.000,00. Taxa de juros alterada para: 1.8% ao mês. Assinado em 2024-05-10."
    )
    (mock_dir / "contrato_original.txt").write_text(
        "Contrato nº 111. Valor total: R$ 40.000,00. Taxa de juros: 1.5% ao mês. Assinado em 2023-01-10."
    )
    (mock_dir / "demonstrativo_divida_v1.txt").write_text(
        "Demonstrativo de Dívida. Valor Principal: R$ 50.000,00. Juros/Encargos: R$ 2.000,00. Total Atualizado: R$ 52.000,00 em 2026-01-15."
    )

    print(f"[1] Testing Subsidios Analysis for {case_id}...")
    
    # Initialize the service and perform the extraction
    service = SubsidioService()
    test_result = service.analyze_process_subsidios(case_id, force_refresh=True)

    # Output the consolidated JSON containing all analyzed documents
    print("\n[2] Extraction Complete! Output JSON:")
    print(test_result.model_dump_json(indent=4))


if __name__ == "__main__":
    run_test()
