import json
from pathlib import Path
from src.monitoring.schemas import CaseProgressionResponse
from src.monitoring.extractor import CaseProgressionExtractor

class MonitoringService:
    def __init__(self, cache_dir: Path = Path("data/monitoring")):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True) 
        self.extractor = CaseProgressionExtractor()

    def scrape_online_case_data(self, process_id: str) -> str:
        """
        PLACEHOLDER: Insert your web scraping logic here.
        Use requests, BeautifulSoup, or Selenium to fetch the online timeline.
        """
        print(f"[DEBUG] Scraping web data for case {process_id}...")
        # Simulate returning raw text scraped from a court website
        return f"Movimentação do processo {process_id} extraída do tribunal. Audiência de conciliação designada para 12/11/2026."

    def get_or_update_case(self, process_id: str, force_refresh: bool = False) -> CaseProgressionResponse:
        json_file_path = self.cache_dir / f"{process_id}.json"

        if json_file_path.exists() and not force_refresh:
            print(f"[DEBUG] Reading cached JSON for {process_id}")
            with open(json_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return CaseProgressionResponse(**data)

        raw_scraped_text = self.scrape_online_case_data(process_id)

        structured_progression = self.extractor.extract_progression(process_id, raw_scraped_text)

        print(f"[DEBUG] Saving new timeline to {json_file_path}")
        with open(json_file_path, "w", encoding="utf-8") as f:
            # .model_dump_json() is the standard for Pydantic v2
            f.write(structured_progression.model_dump_json(indent=4))

        return structured_progression
