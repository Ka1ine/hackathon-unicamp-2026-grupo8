import traceback
from src.monitoring.service import MonitoringService
from src.monitoring.subsidio_service import SubsidioService
from src.monitoring.master_schemas import CaseMasterOverview, ProcessingStatus

class CaseOrchestrator:
    def __init__(self):
        self.timeline_service = MonitoringService()
        self.subsidio_service = SubsidioService()

    def get_full_case_overview(self, process_id: str, url_or_path: str, force_refresh: bool = False) -> CaseMasterOverview:
        overview = CaseMasterOverview(process_id=process_id)
        
        try:
            # 1. Fetch or load timeline safely
            overview.timeline_data = self.timeline_service.get_or_update_case(
                process_id=process_id, 
                url=url_or_path, 
                force_refresh=force_refresh
            )
            
            # 2. Fetch or load document subsidios safely[cite: 1]
            overview.subsidios_data = self.subsidio_service.analyze_process_subsidios(
                process_id=process_id, 
                force_refresh=force_refresh
            )
            
            overview.status = ProcessingStatus.COMPLETED

        except Exception as e:
            print(f"[ERROR] Failed during case orchestration: {e}")
            traceback.print_exc()
            overview.status = ProcessingStatus.FAILED
            overview.error_message = str(e)

        return overview
