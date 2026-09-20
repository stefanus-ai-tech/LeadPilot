from app.schemas import LeadAnalysis, LeadInput, ScoringResult


def score_lead(lead: LeadInput, analysis: LeadAnalysis) -> ScoringResult:
    """Apply the original business rules. Budget is an integer amount in IDR."""
    score = 0
    reasons: list[str] = []

    if lead.budget is not None:
        if lead.budget >= 5_000_000:
            score += 30
            reasons.append("Budget >= Rp5.000.000 (+30)")
        elif lead.budget >= 2_000_000:
            score += 20
            reasons.append("Budget >= Rp2.000.000 (+20)")
        elif lead.budget > 0:
            score += 10
            reasons.append("Budget provided (+10)")

    if lead.company_size is not None:
        if 20 <= lead.company_size <= 200:
            score += 20
            reasons.append("Company size 20-200 (+20)")
        elif lead.company_size >= 5:
            score += 10
            reasons.append("Company size >= 5 (+10)")

    if analysis.service_match:
        score += 20
        reasons.append("Service matches our offering (+20)")
    if analysis.urgency == "high":
        score += 20
        reasons.append("High urgency (+20)")
    elif analysis.urgency == "medium":
        score += 10
        reasons.append("Medium urgency (+10)")
    if analysis.intent == "purchase" and analysis.strong_intent:
        score += 10
        reasons.append("Strong purchase intent (+10)")

    score = min(score, 100)
    tier = "HOT" if score >= 80 else "WARM" if score >= 50 else "COLD"
    return ScoringResult(
        score=score,
        tier=tier,
        requires_human_review=analysis.confidence < 0.60,
        reasons=reasons,
    )
