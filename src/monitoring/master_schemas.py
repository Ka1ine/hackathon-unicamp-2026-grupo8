from enum import Enum
from pydantic import BaseModel, Field
from src.monitoring.schemas import CaseProgressionResponse
from src.monitoring.subsidio_schemas import CompleteSubsidioAnalysis
from typing import Optional

class ProcessingStatus(str, Enum):
    """Tracks the execution state of the orchestration process."""
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"

class CaseMasterOverview(BaseModel):
    """Unified overview containing both timeline progression and document analysis."""
    error_message: Optional[str] = None
    process_id: str = Field(...)
    status: ProcessingStatus = ProcessingStatus.COMPLETED
    subsidios_data: Optional[CompleteSubsidioAnalysis] = None
    timeline_data: Optional[CaseProgressionResponse] = None
