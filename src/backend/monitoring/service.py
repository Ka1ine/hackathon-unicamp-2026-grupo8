import json
from pathlib import Path

from src.backend.monitoring.extractor import CaseProgressionExtractor
from src.backend.monitoring.schemas import CaseProgressionResponse, TimelineEvent
from src.backend.monitoring.scraper import PublicCaseScraper
from src.backend.utils.pdf_utils import extract_text_from_file


class MonitoringService:
    """Handles the retrieval, updating, and caching of case progression data."""

    def __init__(self, base_data_dir: Path = Path("data/example_cases")):
        self.base_data_dir = base_data_dir
        self.extractor = CaseProgressionExtractor()
        self.scraper = PublicCaseScraper()

    def get_or_update_case(
        self, 
        process_id: str, 
        url: str = None, 
        force_refresh: bool = False, 
        parse_local_autos: bool = True,
        demo: bool = False
    ) -> CaseProgressionResponse:
        process_dir = self.base_data_dir / process_id
        process_dir.mkdir(exist_ok=True, parents=True) 
        
        # Change this to save timeline cache in the new "cache" folder
        cache_dir = self.base_data_dir.parent / "cache"
        cache_dir.mkdir(exist_ok=True, parents=True)
        json_file_path = cache_dir / f"_{process_id}_timeline.json"
        
        existing_data = None

        if json_file_path.exists():
            with open(json_file_path, "r", encoding="utf-8") as file_handler:
                existing_data = CaseProgressionResponse(**json.load(file_handler))

        # Return cached data immediately if not forcing a refresh, ensuring it's sorted
        if existing_data and not force_refresh:
            existing_data.timeline.sort(key=lambda x: x.date if x.date else "0000-00-00", reverse=True)
            return existing_data

        all_new_events = []
        latest_stage = None
        latest_action = None
        latest_risk = "Médio"

        # 1. Process Web / Fallback Data (Tagged as "web")
        web_text = ""
        if url:
            print(f"[DEBUG] Attempting live web scrape for {process_id} from {url}...")
            web_text = self.scraper.scrape_jusbrasil_or_public(url)

        if not web_text and demo:
            fallback_path = "data/sample_case.html"
            print(f"[DEBUG] Live web scraping unavailable. Demo mode active: falling back to {fallback_path}")
            web_text = self.scraper.scrape_jusbrasil_or_public(fallback_path)

        if web_text:
            print("[DEBUG] Extracting progression from web/fallback text...")
            web_response = self.extractor.extract_progression(process_id, web_text)
            if web_response and web_response.timeline:
                for ev in web_response.timeline:
                    ev.source = "web"
                    all_new_events.append(ev)
                latest_stage = web_response.current_stage
                latest_action = web_response.next_recommended_action
                latest_risk = web_response.risk_level

        # 2. Process Local File Autos Data (Tagged as "file")
        if parse_local_autos:
            print(f"[DEBUG] Searching for local files in {process_dir}...")
            local_text = ""
            for target_file in process_dir.glob("*.pdf"):
                name_lower = target_file.name.lower()
                if "autos" in name_lower or "processo" in name_lower or "case" in name_lower:
                    print(f"[DEBUG] Extracting text from local file: {target_file.name}")
                    extracted_pdf_text = extract_text_from_file(target_file)
                    if extracted_pdf_text:
                        local_text += extracted_pdf_text + "\n"
            
            if local_text.strip():
                print("[DEBUG] Extracting progression from local files...")
                file_response = self.extractor.extract_progression(process_id, local_text)
                if file_response and file_response.timeline:
                    for ev in file_response.timeline:
                        ev.source = "file"
                        all_new_events.append(ev)
                    if not latest_stage:
                        latest_stage = file_response.current_stage
                        latest_action = file_response.next_recommended_action
                        latest_risk = file_response.risk_level

        if not all_new_events:
            print("[WARN] No data found in URL, fallback, or local files.")
            if existing_data:
                existing_data.timeline.sort(key=lambda x: x.date if x.date else "0000-00-00", reverse=True)
                return existing_data
            
            return CaseProgressionResponse(
                current_stage="Outros",
                next_recommended_action="Aguardar (Nenhuma ação imediata)",
                process_id=process_id,
                timeline=[]
            )

        new_data = CaseProgressionResponse(
            current_stage=latest_stage or "Outros",
            next_recommended_action=latest_action or "Aguardar (Nenhuma ação imediata)",
            process_id=process_id,
            risk_level=latest_risk,
            timeline=all_new_events
        )

        # Merge logic with existing cache file if it was already available
        if existing_data:
            added_count = 0
            existing_events = {(ev.date, ev.title, ev.source) for ev in existing_data.timeline}
            
            for new_event in new_data.timeline:
                if (new_event.date, new_event.title, new_event.source) not in existing_events:
                    existing_data.timeline.append(new_event)
                    added_count += 1
            
            print(f"[DEBUG] Appended {added_count} new events to the existing timeline file.")
            
            existing_data.current_stage = new_data.current_stage
            existing_data.next_recommended_action = new_data.next_recommended_action
            existing_data.risk_level = new_data.risk_level
            
            final_data = existing_data
        else:
            final_data = new_data

        # 3. Sort the combined timeline anti-chronologically (newest dates first)
        # Using "0000-00-00" as a fallback safely pushes items with missing dates to the bottom
        final_data.timeline.sort(key=lambda x: x.date if x.date else "0000-00-00", reverse=True)

        # Save the sorted, merged timeline back to JSON in the process folder
        with open(json_file_path, "w", encoding="utf-8") as file_handler:
            file_handler.write(final_data.model_dump_json(indent=4))

        return final_data