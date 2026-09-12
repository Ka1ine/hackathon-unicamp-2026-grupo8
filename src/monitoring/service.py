import json
from pathlib import Path

from src.monitoring.extractor import CaseProgressionExtractor
from src.monitoring.schemas import CaseProgressionResponse
from src.monitoring.scraper import PublicCaseScraper


class MonitoringService:
    """Handles the retrieval, updating, and caching of case progression data."""

    def __init__(self, base_data_dir: Path = Path("data/processos_exemplo")):
        """Initializes the service to store JSONs in the same directory as the process files."""
        self.base_data_dir = base_data_dir
        self.extractor = CaseProgressionExtractor()
        self.scraper = PublicCaseScraper()

    def get_or_update_case(self, process_id: str, url: str, force_refresh: bool = False) -> CaseProgressionResponse:
        """Fetches new case data, merges it with existing records, and caches the result."""
        # Target the specific process folder
        process_dir = self.base_data_dir / process_id
        process_dir.mkdir(exist_ok=True, parents=True) 
        
        # Save the file directly inside the process folder instead of a global cache
        json_file_path = process_dir / f"{process_id}_timeline.json"
        
        existing_data = None

        # Load existing data if available
        if json_file_path.exists():
            with open(json_file_path, "r", encoding="utf-8") as file_handler:
                existing_data = CaseProgressionResponse(**json.load(file_handler))

        # Return cached data instantly if we aren't forcing a refresh
        if existing_data and not force_refresh:
            return existing_data

        # Scrape the latest online data
        print(f"[DEBUG] Attempting to scrape new data for {process_id} from {url}...")
        raw_scraped_text = self.scraper.scrape_jusbrasil_or_public(url)
        
        # SKIP LOGIC: If page doesn't exist or scraper returns nothing, skip gracefully
        if not raw_scraped_text:
            print("[WARN] Target page not found or empty. Skipping scraping.")
            if existing_data:
                return existing_data
            
            # Return an empty standardized response if no cache and no data exists
            return CaseProgressionResponse(
                current_stage="Outros",
                next_recommended_action="Aguardar (Nenhuma ação imediata)",
                process_id=process_id,
                timeline=[]
            )

        # Extract structured progression using OpenAI
        new_data = self.extractor.extract_progression(process_id, raw_scraped_text)

        # Merge logic: Append only new events
        if existing_data:
            added_count = 0
            existing_events = {(ev.date, ev.title) for ev in existing_data.timeline}
            
            for new_event in new_data.timeline:
                if (new_event.date, new_event.title) not in existing_events:
                    existing_data.timeline.append(new_event)
                    added_count += 1
            
            print(f"[DEBUG] Appended {added_count} new events to the existing timeline.")
            
            # Update root metadata with the most recent LLM analysis
            existing_data.current_stage = new_data.current_stage
            existing_data.next_recommended_action = new_data.next_recommended_action
            existing_data.risk_level = new_data.risk_level
            
            final_data = existing_data
        else:
            final_data = new_data

        # Save the fully merged timeline back to JSON in the process folder
        with open(json_file_path, "w", encoding="utf-8") as file_handler:
            file_handler.write(final_data.model_dump_json(indent=4))

        return final_data