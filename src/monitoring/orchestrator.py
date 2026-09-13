import json
import traceback

from pathlib import Path
from src.monitoring.master_schemas import CaseMasterOverview, ProcessingStatus
from src.monitoring.service import MonitoringService
from src.monitoring.subsidio_service import SubsidioService
from src.policy.policy_service import PolicyService

class CaseOrchestrator:
    """Coordinates the retrieval and merging of case timelines and supporting documents."""

    def __init__(self):
        """Initializes the services required for orchestrating case data."""
        self.subsidio_service = SubsidioService()
        self.timeline_service = MonitoringService()
        self.policy_service = PolicyService()

    def get_full_case_overview(self, process_id: str, url_or_path: str, force_refresh: bool = False) -> CaseMasterOverview:
        """Retrieves a comprehensive overview of a case, including its timeline and documents."""
        # Initialize the unified overview object
        overview = CaseMasterOverview(process_id=process_id)
        
        try:
            # 1. Fetch or load document subsidios safely
            overview.subsidios_data = self.subsidio_service.analyze_process_subsidios(
                force_refresh=force_refresh,
                process_id=process_id
            )
            
            # 2. Fetch or load timeline safely
            overview.timeline_data = self.timeline_service.get_or_update_case(
                force_refresh=force_refresh,
                process_id=process_id, 
                url=url_or_path
            )

            # 3. Predict Policy Decision
            overview.policy_data = self.policy_service.evaluate_case(
                force_refresh=force_refresh, 
                process_id=process_id
            )

            # 4. Save the master overview inside the specific case folder
            process_dir = Path(f"data/example_cases/{process_id}")
            process_dir.mkdir(parents=True, exist_ok=True)
            
            # Change name from _master.json to just _{process_id}.json
            master_cache_path = process_dir / f"_{process_id}.json"
            
            # Convert to dictionary to remove redundant IDs before saving
            output_dict = overview.model_dump()
            if output_dict.get("subsidios_data") and "process_id" in output_dict["subsidios_data"]:
                del output_dict["subsidios_data"]["process_id"]
            if output_dict.get("timeline_data") and "process_id" in output_dict["timeline_data"]:
                del output_dict["timeline_data"]["process_id"]

            with open(master_cache_path, "w", encoding="utf-8") as f:
                json.dump(output_dict, f, indent=4, ensure_ascii=False)

            # Mark as completed if all operations succeed
            overview.status = ProcessingStatus.COMPLETED

        except Exception as e:
            # Handle orchestration failures and capture the error
            print(f"[ERROR] Failed during case orchestration: {e}")
            traceback.print_exc()
            overview.error_message = str(e)
            overview.status = ProcessingStatus.FAILED

        return overview
