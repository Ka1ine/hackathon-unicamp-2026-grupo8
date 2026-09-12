from fastapi import APIRouter, HTTPException, Query
from src.monitoring.schemas import CaseProgressionResponse
from src.monitoring.service import MonitoringService

router = APIRouter(prefix="/api/v1/monitoring", tags=["Monitoring"])
service = MonitoringService()

@router.get("/process/{process_id}", response_model=CaseProgressionResponse)
def get_case_progression(
    process_id: str,
    force_refresh: bool = Query(False, description="Set to true to force a new web scrape")
):
    try:
        return service.get_or_update_case(process_id, force_refresh)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no monitoramento: {str(e)}")
