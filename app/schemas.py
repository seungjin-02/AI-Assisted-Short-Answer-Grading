from datetime import datetime
from typing import Annotated, Any, Literal
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, UUID4

Question = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
Answer = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]
Reason = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=300)]

class GradeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: Question
    reference_answer: Answer
    student_answer: Answer

class GradeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: UUID4
    input: GradeInput

class GradePrediction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision_type: Literal["approve", "reject"]
    confidence: float = Field(strict=True, ge=0, le=1, allow_inf_nan=False)
    reason: Reason

class SignalResponse(BaseModel):
    rule_id: str
    category: str
    score: int
    reason: str
    evidence: dict[str, Any]
    is_critical_override: bool
    metadata: dict[str, Any]

class GradeReview(BaseModel):
    level: str
    risk_score: int
    uncertainty_score: int
    human_required: bool
    recommended_actions: list[str]
    reason_summary: str
    signals: list[SignalResponse]

class GradeRecord(BaseModel):
    alert_id: str
    event_id: str
    request_id: str
    created_at: datetime
    prediction: GradePrediction
    review: GradeReview
    model_version: str
    prompt_version: str
    prompt_hash: str
    ai_latency_ms: int

class GradeResponse(GradeRecord):
    latency_ms: int

class GradeListResponse(BaseModel):
    items: list[GradeRecord]

class ErrorDetail(BaseModel):
    error_type: str
    message: str

class ErrorResponse(BaseModel):
    request_id: str
    error: ErrorDetail