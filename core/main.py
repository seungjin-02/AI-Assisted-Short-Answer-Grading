from .step01_DecisionEvent import DecisionEvent
from .step02_EvaluationContext import build_evaluation_context
from .step03_RuleEvaluation import evaluate_rule
from .step04_SignalGeneration import build_signals
from .step05_ScoreAggregation import summarize_signals
from .step06_GateInterpretation import interpret_gate
from .step07_ReviewSummary import generate_action
from .step08_AlertOutput import AlertOutput, build_alert_output

def evaluate_event(event: DecisionEvent) -> AlertOutput:
    context = build_evaluation_context(event)
    evaluations = evaluate_rule(event, context)
    signals = build_signals(evaluations)
    signal_summary = summarize_signals(signals)
    decision = interpret_gate(signal_summary, context.rubric_decision)
    action = generate_action(decision, signals, rubric_decision=context.rubric_decision)

    return build_alert_output(
        event=event,
        signals=signals,
        signal_summary=signal_summary,
        decision=decision,
        action=action,
        rubric_decision=context.rubric_decision,
    )
