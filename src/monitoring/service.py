import json
from pathlib import Path
from src.monitoring.schemas import CaseProgressionResponse
from src.monitoring.extractor import CaseProgressionExtractor
from src.monitoring.scraper import PublicCaseScraper

class MonitoringService:
    def __init__(self, cache_dir: Path = Path("data/monitoramento_cache")):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True) 
        self.extractor = CaseProgressionExtractor()
        self.scraper = PublicCaseScraper()

    def get_or_update_case(self, process_id: str, url: str, force_refresh: bool = False) -> CaseProgressionResponse:
        json_file_path = self.cache_dir / f"{process_id}.json"
        existing_data = None

        # 1. Load existing data if available
        if json_file_path.exists():
            with open(json_file_path, "r", encoding="utf-8") as f:
                existing_data = CaseProgressionResponse(**json.load(f))

        # 2. Return cached data instantly if we aren't forcing a refresh
        if existing_data and not force_refresh:
            return existing_data

        # 3. Scrape the latest online data
        print(f"[DEBUG] Scraping new data for {process_id}...")
        raw_scraped_text = self.scraper.scrape_jusbrasil_or_public(url)
        
        if not raw_scraped_text:
            print("[WARN] Scraper returned empty text. Returning existing data if available.")
            return existing_data if existing_data else None

        # 4. Extract structured progression using OpenAI
        new_data = self.extractor.extract_progression(process_id, raw_scraped_text)

        # 5. Merge logic: Append only new events
        if existing_data:
            # Create a set of existing (date, title) to quickly check for duplicates
            existing_events = {(ev.date, ev.title) for ev in existing_data.timeline}
            
            added_count = 0
            for new_event in new_data.timeline:
                if (new_event.date, new_event.title) not in existing_events:
                    existing_data.timeline.append(new_event)
                    added_count += 1
            
            print(f"[DEBUG] Appended {added_count} new events to the existing timeline.")
            
            # Update root metadata with the most recent LLM analysis
            existing_data.current_stage = new_data.current_stage
            existing_data.risk_level = new_data.risk_level
            existing_data.next_recommended_action = new_data.next_recommended_action
            
            final_data = existing_data
        else:
            final_data = new_data

        # 6. Save the fully merged timeline back to JSON
        with open(json_file_path, "w", encoding="utf-8") as f:
            f.write(final_data.model_dump_json(indent=4))

        return final_data
