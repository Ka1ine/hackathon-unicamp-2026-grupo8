import traceback

from src.monitoring.master_schemas import CaseMasterOverview, ProcessingStatus
from src.monitoring.service import MonitoringService
from src.monitoring.subsidio_service import SubsidioService

class CaseOrchestrator:
    """Coordinates the retrieval and merging of case timelines and supporting documents."""

    def __init__(self):
        """Initializes the services required for orchestrating case data."""
        self.subsidio_service = SubsidioService()
        self.timeline_service = MonitoringService()

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
            
            # Mark as completed if both operations succeed
            overview.status = ProcessingStatus.COMPLETED

        except Exception as e:
            # Handle orchestration failures and capture the error
            print(f"[ERROR] Failed during case orchestration: {e}")
            traceback.print_exc()
            overview.error_message = str(e)
            overview.status = ProcessingStatus.FAILED

        return overview
