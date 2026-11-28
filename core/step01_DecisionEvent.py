from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NonBlank = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
DecisionType = Literal["approve", "reject"]

# 필수 조건 하나의 판정: 충족 / 언급 없음 / 반대 내용 / 의미 불명확
CriterionStatus = Literal["satisfied", "not_addressed", "contradicted", "unclear"]

class CriterionAssessment(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    criterion_id: NonBlank
    status: CriterionStatus
    quote_found: bool | None # 학생 답안에서 인용문을 찾으면 True, 못 찾으면 False, 확인 대상이 아니면 None

    @model_validator(mode="after")
    def validate_quote_check(self) -> Self:
        needs_quote = self.status in {"satisfied", "contradicted"}

        # 인용 확인이 필요한데 결과가 없는 경우
        if needs_quote and self.quote_found is None:
            raise ValueError("A quotation check result is required.")

        # 인용 확인이 필요 없는데 결과가 있는 경우
        if not needs_quote and self.quote_found is not None:
            raise ValueError("quote_found must be None for this status.")

        return self

class GradingContext(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    # [, ...] 같은 타입 여러개 담겠다는 문법

    # 서버가 필수 조건에 붙여 Gemini에 보낸 ID 목록
    required_condition_ids: tuple[NonBlank, ...] = Field(min_length=1)

    # Gemini가 돌려준 조건별 판정에 서버의 인용 확인 결과를 더한 목록
    assessments: tuple[CriterionAssessment, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_condition_ids(self) -> Self:
        required_ids = set(self.required_condition_ids)
        if len(required_ids) != len(self.required_condition_ids):
            raise ValueError("Required condition IDs must be unique.")

        assessed_ids = {item.criterion_id for item in self.assessments}
        if assessed_ids != required_ids or len(self.assessments) != len(required_ids):
            raise ValueError("Each required condition must have exactly one assessment.")
        return self

class DecisionEvent(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    event_id: NonBlank
    decision_type: DecisionType
    confidence: float = Field(ge=0, le=1, allow_inf_nan=False)
    grading: GradingContext
