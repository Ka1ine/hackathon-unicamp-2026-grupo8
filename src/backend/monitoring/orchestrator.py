import json
import traceback

from pathlib import Path
from src.backend.monitoring.master_schemas import CaseMasterOverview, ProcessingStatus
from src.backend.monitoring.service import MonitoringService
from src.backend.monitoring.subsidio_service import SubsidioService
from src.backend.policy.policy_service import PolicyService

class CaseOrchestrator:
    """Coordinates the retrieval and merging of case timelines and supporting documents."""

    def __init__(self):
        """Initializes the services required for orchestrating case data."""
        self.timeline_service = MonitoringService()
        self.policy_service = PolicyService()

    def get_full_case_overview(self, process_id: str, url_or_path: str, force_refresh: bool = False, nivel_slider: float = 0.50) -> CaseMasterOverview:
        """Retrieves a comprehensive overview of a case, including its timeline and documents."""
        # Initialize the unified overview object
        overview = CaseMasterOverview(process_id=process_id)
        
        try:
            # 2. Fetch or load timeline safely
            overview.timeline_data = self.timeline_service.get_or_update_case(
                force_refresh=force_refresh,
                process_id=process_id, 
                url=url_or_path
            )

            # 3. Predict Policy Decision
            overview.policy_data = self.policy_service.evaluate_case(
                force_refresh=force_refresh, 
                process_id=process_id,
                nivel_slider=nivel_slider
            )

            # 4. Save the master overview inside the specific case folder
            process_dir = Path(f"data/example_cases/{process_id}")
            process_dir.mkdir(parents=True, exist_ok=True)
            
            # Incorporamos o valor do slider no cache master também, para não sobrescrever decisões diferentes 
            slider_str = str(nivel_slider).replace('.', '')
            master_cache_path = process_dir / f"_{process_id}_{slider_str}.json"
            
            # Convert to dictionary to remove redundant IDs before saving
            output_dict = overview.model_dump(exclude_none=True)

            # Keep only the timeline cleanups
            if output_dict.get("timeline_data"):
                if "process_id" in output_dict["timeline_data"]:
                    del output_dict["timeline_data"]["process_id"]
                if "risk_level" in output_dict["timeline_data"]:
                    del output_dict["timeline_data"]["risk_level"]

            with open(master_cache_path, "w", encoding="utf-8") as f:
                json.dump(output_dict, f, indent=4, ensure_ascii=False)

            overview.status = ProcessingStatus.COMPLETED

        except Exception as e:
            # Handle orchestration failures and capture the error
            print(f"[ERROR] Failed during case orchestration: {e}")
            traceback.print_exc()
            overview.error_message = str(e)
            overview.status = ProcessingStatus.FAILED

        return overview
