from dataclasses import dataclass

from .step01_DecisionEvent import DecisionEvent, DecisionType

@dataclass(frozen=True)
class EvaluationContext:
    rubric_decision: DecisionType | None
    rubric_reason: str

def build_evaluation_context(event: DecisionEvent) -> EvaluationContext:
    assessments = event.grading.assessments

    # 필수 조건을 언급하지 않았거나 반대 판정에 사용한 인용이 확인된 경우
    missing_ids = [item.criterion_id for item in assessments if item.status == "not_addressed"]
    contradicted_ids = [item.criterion_id for item in assessments if item.status == "contradicted" and item.quote_found is True]

    if missing_ids or contradicted_ids:
        reasons: list[str] = []
        if missing_ids:
            reasons.append(f"필수 조건 언급 없음 ({', '.join(missing_ids)})")
        if contradicted_ids:
            reasons.append(f"필수 조건과 반대되는 내용 확인 ({', '.join(contradicted_ids)})")

        return EvaluationContext(
            rubric_decision="reject",
            rubric_reason=" · ".join(reasons),
        )

    if all(item.status == "satisfied" and item.quote_found is True for item in assessments):
        return EvaluationContext(
            rubric_decision="approve",
            rubric_reason="모든 필수 조건이 충족으로 판정됐고 인용문이 원문에서 확인됨",
        )

    return EvaluationContext(
        rubric_decision=None,
        rubric_reason="일부 필수 조건의 충족 여부를 확정할 수 없음",
    )