from dataclasses import dataclass

from .step02_EvaluationContext import EvaluationContext
from .step04_SignalGeneration import Signal
from .step06_GateInterpretation import GateDecision

def build_reason_summary(context: EvaluationContext, signals: list[Signal]) -> str:
    decision_labels = {
        "approve": "기준상 인정",
        "reject": "기준상 불인정",
        None: "기준상 판정 보류",
    }

    reasons = [decision_labels[context.rubric_decision], context.rubric_reason]
    reasons.extend(signal.reason for signal in signals)

    return " · ".join(reasons)