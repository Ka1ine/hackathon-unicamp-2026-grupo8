from src.monitoring.service import MonitoringService

def run_test():
    # Path to your local HTML file inside the data directory
    local_html_path = "data/sample_case.html"
    process_id = "ADI_4439"
    
    service = MonitoringService()
    
    print("--- EXECUÇÃO 1: Processing Local File ---")
    resultado = service.get_or_update_case(process_id, local_html_path, force_refresh=True)
    
    if resultado:
        print(f"\nTotal de eventos extraídos: {len(resultado.timeline)}")
        print(f"Próxima Ação: {resultado.next_recommended_action}")
        print("\nJSON de saída gerado com sucesso:")
        print(resultado.model_dump_json(indent=4))
    else:
        print("[ERRO] Não foi possível extrair dados do arquivo fornecido.")

if __name__ == "__main__":
    run_test()
