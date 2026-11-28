from dataclasses import dataclass, field
from typing import Any

from .step03_RuleEvaluation import RuleEvaluation

@dataclass(frozen=True)
class Signal:
    rule_id: str
    category: str
    score: int
    reason: str
    evidence: dict[str, Any] = field(default_factory=dict)
    is_critical_override: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

def build_signals(evaluations: list[RuleEvaluation]) -> list[Signal]:
    signals = []
    for evaluation in evaluations:
        if evaluation.evidence is None:
            continue
        rule = evaluation.rule
        signals.append(Signal(
            rule_id=rule.rule_id,
            category=rule.category,
            score=rule.score,
            reason=rule.reason,
            evidence=evaluation.evidence,
        ))
    return signals
