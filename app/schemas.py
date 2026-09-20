from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class LeadInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    company: str = Field(default="", max_length=300)
    company_size: int | None = Field(default=None, ge=1, strict=True)
    budget: int | None = Field(default=None, ge=0, strict=True)
    service: str = Field(default="", max_length=500)
    timeline: str = Field(default="", max_length=300)
    message: str = Field(min_length=5, max_length=8000)
    source: str = Field(default="website", max_length=200)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        return value.strip().lower() if isinstance(value, str) else value


class LeadAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)

    intent: Literal["purchase", "research", "support", "spam", "unknown"]
    urgency: Literal["high", "medium", "low", "unknown"]
    category: str = Field(min_length=1, max_length=200)
    service_match: bool
    strong_intent: bool
    clear_requirement: bool
    budget_mentioned: bool
    summary: str = Field(min_length=1, max_length=1000)
    confidence: float = Field(ge=0, le=1, allow_inf_nan=False)


class ScoringResult(BaseModel):
    score: int = Field(ge=0, le=100)
    tier: Literal["HOT", "WARM", "COLD"]
    requires_human_review: bool
    reasons: list[str]


class TriageResult(BaseModel):
    lead: LeadInput
    analysis: LeadAnalysis
    scoring: ScoringResult
