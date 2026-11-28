from dataclasses import dataclass

from .step01_DecisionEvent import DecisionEvent, DecisionType
from .step04_SignalGeneration import Signal
from .step05_ScoreAggregation import SignalSummary
from .step06_GateInterpretation import GateDecision

@dataclass(frozen=True)
class AlertOutput:
    event_id: str
    rubric_decision: DecisionType | None
    level: str
    risk_score: int
    uncertainty_score: int
    human_required: bool
    reason_summary: str
    signals: list[Signal]

def build_alert_output(
    event: DecisionEvent,
    signals: list[Signal],
    signal_summary: SignalSummary,
    decision: GateDecision,
    *,
    rubric_decision: DecisionType | None,
    reason_summary: str,
) -> AlertOutput:
    return AlertOutput(
        event_id=event.event_id,
        rubric_decision=rubric_decision,
        level=decision.final_level.value,
        risk_score=signal_summary.risk_score,
        uncertainty_score=signal_summary.uncertainty_score,
        human_required=decision.human_required,
        reason_summary=reason_summary,
        signals=signals,
    )