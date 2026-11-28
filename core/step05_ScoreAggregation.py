from dataclasses import dataclass

from .step04_SignalGeneration import Signal

@dataclass(frozen=True)
class SignalSummary:
    risk_score: int
    uncertainty_score: int

def summarize_signals(signals: list[Signal]) -> SignalSummary:
    return SignalSummary(
        risk_score=sum(signal.score for signal in signals if signal.category == "risk"),
        uncertainty_score=sum(signal.score for signal in signals if signal.category == "uncertainty"),
    )
