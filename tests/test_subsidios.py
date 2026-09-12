from pathlib import Path
from dotenv import load_dotenv
from src.monitoring.subsidio_service import SubsidioService

load_dotenv()

def run_test():
    test_process_id = "test_subsidios"
    
    mock_dir = Path("data/subsidios") / test_process_id
    mock_dir.mkdir(parents=True, exist_ok=True)
    
    # Criando múltiplos arquivos do mesmo tipo
    (mock_dir / "contrato_original.txt").write_text(
        "Contrato nº 111. Valor total: R$ 40.000,00. Taxa de juros: 1.5% ao mês. Assinado em 2023-01-10."
    )
    (mock_dir / "contrato_aditivo.txt").write_text(
        "Aditivo ao Contrato nº 111. Novo valor total: R$ 50.000,00. Taxa de juros alterada para: 1.8% ao mês. Assinado em 2024-05-10."
    )
    (mock_dir / "demonstrativo_divida_v1.txt").write_text(
        "Demonstrativo de Dívida. Valor Principal: R$ 50.000,00. Juros/Encargos: R$ 2.000,00. Total Atualizado: R$ 52.000,00 em 2026-01-15."
    )

    print(f"[1] Testing Subsidios Analysis for {test_process_id}...")
    service = SubsidioService()
    result = service.analyze_process_subsidios(test_process_id, force_refresh=True)

    print("\n[2] Extraction Complete! Output JSON:")
    print(result.model_dump_json(indent=4))

if __name__ == "__main__":
    run_test()