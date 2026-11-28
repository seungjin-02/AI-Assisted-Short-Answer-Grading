from dataclasses import dataclass
from typing import Any, Callable, Literal

from .step01_DecisionEvent import DecisionEvent
from .step02_EvaluationContext import EvaluationContext

RuleEvidence = Callable[[DecisionEvent, EvaluationContext], dict[str, Any] | None]
LOW_CONFIDENCE_THRESHOLD = 0.70

@dataclass(frozen=True)
class Rule:
    rule_id: str
    category: Literal["risk", "uncertainty"]
    score: int
    reason: str
    evidence_for: RuleEvidence

@dataclass(frozen=True)
class RuleEvaluation:
    rule: Rule
    evidence: dict[str, Any] | None

def grading_decision_conflict(event: DecisionEvent, context: EvaluationContext) -> dict[str, Any] | None:
    rubric_decision = context.rubric_decision
    if rubric_decision is None or event.decision_type == rubric_decision:
        return None

    if rubric_decision == "reject":
        # 기준상 reject의 근거가 된 조건 ID를 남긴다
        condition_ids = [
            item.criterion_id for item in event.grading.assessments if item.status == "not_addressed" or (item.status == "contradicted" and item.quote_found is True)
        ]
    else:
        # 기준상 approve는 모든 필수 조건을 충족했다는 뜻이다
        condition_ids = list(event.grading.required_condition_ids)

    return {
        "decision_type": event.decision_type,
        "rubric_decision": rubric_decision,
        "condition_ids": condition_ids,
    }

def grading_evidence_unverified(event: DecisionEvent, context: EvaluationContext) -> dict[str, Any] | None:
    condition_ids = [
        item.criterion_id for item in event.grading.assessments if item.quote_found is False
    ]
    return {"condition_ids": condition_ids} if condition_ids else None

def grading_condition_uncertain(event: DecisionEvent, context: EvaluationContext) -> dict[str, Any] | None:
    if context.rubric_decision is not None:
        return None

    condition_ids = [
        item.criterion_id for item in event.grading.assessments if item.status == "unclear"
    ]
    return {"condition_ids": condition_ids} if condition_ids else None


def grading_low_confidence(event: DecisionEvent, context: EvaluationContext) -> dict[str, Any] | None:
    if event.confidence > LOW_CONFIDENCE_THRESHOLD:
        return None

    # 조건 판단 보류로 uncertainty를 이미 반영했다면 중복 반영 x
    if grading_condition_uncertain(event, context) is not None:
        return None

    return {
        "decision_type": event.decision_type,
        "confidence": event.confidence,
        "threshold": LOW_CONFIDENCE_THRESHOLD,
    }

GRADING_RULES = (
    Rule(
        rule_id="grading_decision_conflict",
        category="risk",
        score=1,
        reason="AI 제안과 필수 조건에 따른 판정이 충돌함",
        evidence_for=grading_decision_conflict,
    ),
    Rule(
        rule_id="grading_evidence_unverified",
        category="risk",
        score=1,
        reason="AI가 제시한 인용문을 학생 답안에서 확인할 수 없음",
        evidence_for=grading_evidence_unverified,
    ),
    Rule(
        rule_id="grading_condition_uncertain",
        category="uncertainty",
        score=1,
        reason="필수 조건의 충족 여부가 모호해 판정을 보류함",
        evidence_for=grading_condition_uncertain,
    ),
    Rule(
        rule_id="grading_low_confidence",
        category="uncertainty",
        score=1,
        reason="AI가 낮은 확신으로 채점을 제안함",
        evidence_for=grading_low_confidence,
    ),
)

def evaluate_rule(event: DecisionEvent, context: EvaluationContext) -> list[RuleEvaluation]:
    return [
        RuleEvaluation(rule=rule, evidence=rule.evidence_for(event, context)) for rule in GRADING_RULES
    ]