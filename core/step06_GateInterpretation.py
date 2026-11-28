from dataclasses import dataclass
from enum import Enum

from .step01_DecisionEvent import DecisionType
from .step05_ScoreAggregation import SignalSummary

class RiskLevel(str, Enum):
    INFO = "INFO"
    WARN = "WARN"

@dataclass(frozen=True)
class GateDecision:
    final_level: RiskLevel
    human_required: bool

def interpret_gate(inputs: SignalSummary, rubric_decision: DecisionType | None,) -> GateDecision:
    human_required = (
        rubric_decision is None or inputs.risk_score > 0 or inputs.uncertainty_score > 0
    )

    return GateDecision(
        final_level=RiskLevel.WARN if human_required else RiskLevel.INFO,
        human_required=human_required,
    )