from src.monitoring.service import MonitoringService

def run_test():
    """Executes a test scrape against a local sample HTML file to validate the extraction process."""
    # Define test parameters and initialize the service
    local_html_path = "data/sample_case.html"
    process_id = "test_scrape"
    service = MonitoringService()
    
    print("--- EXECUÇÃO 1: Processing Local File ---")
    
    # Execute the scraping and extraction workflow
    test_result = service.get_or_update_case(process_id, local_html_path, force_refresh=True)
    
    # Evaluate and display the extraction results
    if test_result:
        print(f"\nTotal de eventos extraídos: {len(test_result.timeline)}")
        print(f"Próxima Ação: {test_result.next_recommended_action}")
        print("\nJSON de saída gerado com sucesso:")
        print(test_result.model_dump_json(indent=4))
    else:
        print("[ERRO] Não foi possível extrair dados do arquivo fornecido.")

if __name__ == "__main__":
    run_test()
