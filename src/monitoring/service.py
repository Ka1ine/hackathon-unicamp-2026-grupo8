import json
from pathlib import Path

from src.monitoring.extractor import CaseProgressionExtractor
from src.monitoring.schemas import CaseProgressionResponse
from src.monitoring.scraper import PublicCaseScraper
from src.utils.pdf_utils import extract_text_from_file  # <-- Added import


class MonitoringService:
    """Handles the retrieval, updating, and caching of case progression data."""

    def __init__(self, base_data_dir: Path = Path("data/processos_exemplo")):
        self.base_data_dir = base_data_dir
        self.extractor = CaseProgressionExtractor()
        self.scraper = PublicCaseScraper()

    def get_or_update_case(self, process_id: str, url: str, force_refresh: bool = False, parse_local_autos: bool = True) -> CaseProgressionResponse:
        process_dir = self.base_data_dir / process_id
        process_dir.mkdir(exist_ok=True, parents=True) 
        
        json_file_path = process_dir / f"{process_id}_timeline.json"
        existing_data = None

        if json_file_path.exists():
            with open(json_file_path, "r", encoding="utf-8") as file_handler:
                existing_data = CaseProgressionResponse(**json.load(file_handler))

        if existing_data and not force_refresh:
            return existing_data

        # Initialize an empty string to accumulate all gathered text
        raw_combined_text = ""

        # 1. Optionally scrape web/external data
        if url:
            print(f"[DEBUG] Attempting to scrape new data for {process_id} from {url}...")
            web_text = self.scraper.scrape_jusbrasil_or_public(url)
            if web_text:
                raw_combined_text += web_text + "\n"

        # 2. NEW LOGIC: Scan local process folder for the case progression PDF
        if parse_local_autos:
            print(f"[DEBUG] Searching for local 'Autos' files in {process_dir}...")
            for target_file in process_dir.glob("*.pdf"):
                # Case-insensitive check to identify the core process document
                if "autos" in target_file.name.lower() or "processo" in target_file.name.lower():
                    print(f"[DEBUG] Extracting timeline from local file: {target_file.name}")
                    extracted_pdf_text = extract_text_from_file(target_file)
                    if extracted_pdf_text:
                        raw_combined_text += extracted_pdf_text + "\n"

        # SKIP LOGIC: If no text was found anywhere, return existing data or empty schema
        if not raw_combined_text.strip():
            print("[WARN] No data found in URL or local files. Skipping extraction.")
            if existing_data:
                return existing_data
            
            return CaseProgressionResponse(
                current_stage="Outros",
                next_recommended_action="Aguardar (Nenhuma ação imediata)",
                process_id=process_id,
                timeline=[]
            )

        # Extract structured progression using OpenAI with the combined text
        new_data = self.extractor.extract_progression(process_id, raw_combined_text)

        # Merge logic: Append only new events
        if existing_data:
            added_count = 0
            existing_events = {(ev.date, ev.title) for ev in existing_data.timeline}
            
            for new_event in new_data.timeline:
                if (new_event.date, new_event.title) not in existing_events:
                    existing_data.timeline.append(new_event)
                    added_count += 1
            
            print(f"[DEBUG] Appended {added_count} new events to the existing timeline.")
            
            existing_data.current_stage = new_data.current_stage
            existing_data.next_recommended_action = new_data.next_recommended_action
            existing_data.risk_level = new_data.risk_level
            
            final_data = existing_data
        else:
            final_data = new_data

        # Save to JSON
        with open(json_file_path, "w", encoding="utf-8") as file_handler:
            file_handler.write(final_data.model_dump_json(indent=4))

        return final_data