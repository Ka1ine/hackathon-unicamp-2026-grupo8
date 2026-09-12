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

from fastapi import APIRouter, HTTPException, Query
from src.monitoring.subsidio_schemas import CompleteSubsidioAnalysis
from src.monitoring.subsidio_service import SubsidioService

router = APIRouter(prefix="/api/v1/monitoring", tags=["Monitoring"])
subsidio_service = SubsidioService()

@router.get("/process/{process_id}/subsidios", response_model=CompleteSubsidioAnalysis)
def get_process_subsidios(
    process_id: str,
    force_refresh: bool = Query(False, description="Força o reprocessamento dos arquivos de subsídio")
):
    try:
        return subsidio_service.analyze_process_subsidios(process_id, force_refresh)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao analisar subsídios: {str(e)}")

from src.monitoring.orchestrator import CaseOrchestrator
from src.monitoring.master_schemas import CaseMasterOverview

orchestrator = CaseOrchestrator()

@router.get("/process/{process_id}/full", response_model=CaseMasterOverview)
def get_full_case_overview(
    process_id: str, 
    source_path: str = "data/sample_case.html",
    force_refresh: bool = False
):
    """
    Unified endpoint: Returns both the timeline progression and supporting document analysis.
    Uses local cache to avoid redundant OpenAI/scraping calls.
    """
    return orchestrator.get_full_case_overview(
        process_id=process_id, 
        url_or_path=source_path, 
        force_refresh=force_refresh
    )
