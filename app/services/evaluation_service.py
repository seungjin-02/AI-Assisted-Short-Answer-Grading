from dataclasses import asdict
from datetime import datetime, timezone
from uuid import uuid4

from app.schemas import GradeRecord, GradeReview
from app.services.grading_service import GradeModelResult
from core.main import evaluate_event
from core.step01_DecisionEvent import DecisionEvent

def evaluate_grade(request_id: str, model_result: GradeModelResult) -> GradeRecord:
    prediction = model_result.prediction

    event = DecisionEvent(
        event_id=str(uuid4()),
        decision_type=prediction.decision_type,
        confidence=prediction.confidence,
        latency_ms=model_result.ai_latency_ms,
        model_version=model_result.model_version,
        error_code=None,
        metadata={"grade_reason": prediction.reason},
    )

    alert = evaluate_event(event)
    review = GradeReview.model_validate(asdict(alert))

    return GradeRecord(
        alert_id=request_id,
        event_id=event.event_id,
        request_id=request_id,
        created_at=datetime.now(timezone.utc),
        prediction=prediction,
        review=review,
        model_version=model_result.model_version,
        prompt_version=model_result.prompt_version,
        prompt_hash=model_result.prompt_hash,
        ai_latency_ms=model_result.ai_latency_ms,
    )