from app.llm import analyze_lead
from app.schemas import LeadInput, TriageResult
from app.scoring import score_lead
from app.validation import normalize_lead


def triage_lead(lead: LeadInput) -> TriageResult:
    normalized = normalize_lead(lead)
    analysis = analyze_lead(normalized)
    return TriageResult(
        lead=normalized,
        analysis=analysis,
        scoring=score_lead(normalized, analysis),
    )
