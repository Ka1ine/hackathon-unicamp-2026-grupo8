from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from src.monitoring.schemas import CaseProgressionResponse
from src.monitoring.subsidio_schemas import CompleteSubsidioAnalysis

class ProcessingStatus(str, Enum):
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"

class CaseMasterOverview(BaseModel):
    process_id: str
    status: ProcessingStatus = ProcessingStatus.COMPLETED
    error_message: Optional[str] = None
    timeline_data: Optional[CaseProgressionResponse] = None
    subsidios_data: Optional[CompleteSubsidioAnalysis] = None
