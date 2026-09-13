from enum import Enum
from pydantic import BaseModel, Field
from src.backend.monitoring.schemas import CaseProgressionResponse
from src.backend.monitoring.subsidio_schemas import CompleteSubsidioAnalysis
from src.backend.policy.policy_schemas import PolicyDecision
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
    policy_data: Optional[PolicyDecision] = None
    timeline_data: Optional[CaseProgressionResponse] = None
