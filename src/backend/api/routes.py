import json

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Literal
from src.backend.monitoring.assistant_service import AssistantAnswer, ProcessAssistantService
from src.backend.monitoring.master_schemas import CaseMasterOverview
from src.backend.monitoring.orchestrator import CaseOrchestrator
from src.backend.monitoring.schemas import CaseProgressionResponse
from src.backend.monitoring.service import MonitoringService
from src.backend.monitoring.subsidio_schemas import CompleteSubsidioAnalysis
from src.backend.monitoring.subsidio_service import SubsidioService
from src.backend.policy.policy_schemas import PolicyDecision

# -----------------------------------------------------------------------------
# Module Variables
# -----------------------------------------------------------------------------
orchestrator = CaseOrchestrator()
router = APIRouter(prefix="/api/v1/monitoring", tags=["Monitoring"])
service = MonitoringService()
subsidio_service = SubsidioService()
assistant_service = ProcessAssistantService()


class AssistantHistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ProcessAssistantRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[AssistantHistoryItem] = Field(default_factory=list, max_length=8)

# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------

@router.get("/process/{process_id}", response_model=CaseProgressionResponse)
def get_case_progression(
    process_id: str,
    force_refresh: bool = Query(False, description="Set to true to force a new extraction"),
    parse_local_autos: bool = Query(True, description="Set to true to read 'Autos do Processo' PDFs in the local folder")
):
    """
    Fetches the timeline progression of a specific case.
    Uses local cache unless force_refresh is requested.
    """
    try:
        return service.get_or_update_case(
            process_id=process_id, 
            url="data/sample_case.html", 
            force_refresh=force_refresh,
            parse_local_autos=parse_local_autos
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no monitoramento: {str(e)}")

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
    try:
        return orchestrator.get_full_case_overview(
            process_id=process_id, 
            url_or_path=source_path, 
            force_refresh=force_refresh
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no master overview: {str(e)}")


@router.get("/process/{process_id}/policy", response_model=PolicyDecision)
def get_process_policy(
    process_id: str,
    aggressiveness: int = Query(50, ge=0, le=100, description="Percentual de agressividade da política"),
):
    """Calcula a política do processo com a preferência decisória informada."""
    try:
        return orchestrator.policy_service.evaluate_case(
            process_id=process_id,
            aggressiveness=aggressiveness,
        )
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular a política: {error}")


@router.post("/process/{process_id}/policy", response_model=PolicyDecision)
def update_process_policy(
    process_id: str,
    aggressiveness: int = Query(50, ge=0, le=100, description="Percentual de agressividade da política"),
):
    """Recalcula a política e atualiza o JSON consolidado do processo."""
    try:
        return orchestrator.policy_service.update_case_policy(
            process_id=process_id,
            aggressiveness=aggressiveness,
        )
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except (json.JSONDecodeError, OSError) as error:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar o JSON do processo: {error}")
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar a política: {error}")


@router.get("/process/{process_id}/subsidios", response_model=CompleteSubsidioAnalysis)
def get_process_subsidios(
    process_id: str,
    force_refresh: bool = Query(False, description="Força o reprocessamento dos arquivos de subsídio")
):
    """
    Analyzes and returns data extracted from the supporting documents (subsídios) for a specific case.
    """
    try:
        return subsidio_service.analyze_process_subsidios(process_id, force_refresh)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao analisar subsídios: {str(e)}")


@router.post("/process/{process_id}/assistant", response_model=AssistantAnswer)
def ask_process_assistant(process_id: str, request: ProcessAssistantRequest):
    """Answers a question using only the PDFs and monitoring JSON of one process."""
    try:
        return assistant_service.answer(
            process_id=process_id,
            message=request.message,
            history=[item.model_dump() for item in request.history],
        )
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Não foi possível gerar uma resposta para este processo. Tente novamente.",
        )
