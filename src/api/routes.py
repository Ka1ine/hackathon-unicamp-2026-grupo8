from fastapi import APIRouter, HTTPException
from src.monitoring.schemas import CaseProgressionResponse
from src.monitoring.service import MonitoringService

router = APIRouter(prefix="/api/v1/monitoring", tags=["Monitoring"])
service = MonitoringService()

@router.get("/process/{process_id}", response_model=CaseProgressionResponse)
def get_case_progression(process_id: str):
    try:
        return service.analyze_case(process_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar linha do tempo: {str(e)}")
    