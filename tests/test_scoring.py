import pytest

from app.schemas import LeadAnalysis, LeadInput
from app.scoring import score_lead


def quiet_analysis(data, **changes):
    return LeadAnalysis(**(data | dict(intent="research", urgency="unknown", service_match=False,
                                      strong_intent=False) | changes))


@pytest.mark.parametrize("budget,expected", [(None, 0), (0, 0), (1, 10), (1_999_999, 10),
                                              (2_000_000, 20), (4_999_999, 20), (5_000_000, 30)])
def test_budget_boundaries(lead_data, analysis_data, budget, expected):
    lead = LeadInput(**lead_data, budget=budget)
    assert score_lead(lead, quiet_analysis(analysis_data)).score == expected


@pytest.mark.parametrize("size,expected", [(None, 0), (1, 0), (4, 0), (5, 10), (19, 10),
                                         (20, 20), (200, 20), (201, 10)])
def test_company_boundaries(lead_data, analysis_data, size, expected):
    assert score_lead(LeadInput(**lead_data, company_size=size), quiet_analysis(analysis_data)).score == expected


@pytest.mark.parametrize("urgency,expected", [("unknown", 0), ("low", 0), ("medium", 10), ("high", 20)])
def test_urgency(lead, analysis_data, urgency, expected):
    assert score_lead(lead, quiet_analysis(analysis_data, urgency=urgency)).score == expected


@pytest.mark.parametrize("intent,strong,expected", [("purchase", True, 10), ("purchase", False, 0),
    ("research", True, 0), ("support", True, 0), ("spam", True, 0), ("unknown", True, 0)])
def test_purchase_requires_both_signals(lead, analysis_data, intent, strong, expected):
    assert score_lead(lead, quiet_analysis(analysis_data, intent=intent, strong_intent=strong)).score == expected


def test_service_match(lead, analysis_data):
    result = score_lead(lead, quiet_analysis(analysis_data, service_match=True))
    assert result.score == 20


@pytest.mark.parametrize("budget,size,urgency,strong,expected,tier", [
    (5_000_000, 50, "high", True, 100, "HOT"),
    (1_000_000, 10, "medium", False, 50, "WARM"),
    (None, None, "high", False, 40, "COLD"),
    (5_000_000, None, "medium", True, 70, "WARM"),
    (5_000_000, None, "high", True, 80, "HOT"),
])
def test_scores_and_tiers(lead_data, analysis_data, budget, size, urgency, strong, expected, tier):
    lead = LeadInput(**lead_data, budget=budget, company_size=size)
    analysis = LeadAnalysis(**(analysis_data | dict(urgency=urgency, strong_intent=strong)))
    result = score_lead(lead, analysis)
    assert (result.score, result.tier) == (expected, tier)
    assert sum(int(reason.rsplit("(+", 1)[1].rstrip(")")) for reason in result.reasons) == expected
    assert score_lead(lead, analysis) == result


@pytest.mark.parametrize("confidence,review", [(0, True), (0.599, True), (0.6, False), (1, False)])
def test_confidence_boundary(lead, analysis_data, confidence, review):
    analysis = LeadAnalysis(**(analysis_data | {"confidence": confidence}))
    assert score_lead(lead, analysis).requires_human_review is review


def test_budget_in_message_does_not_invent_numeric_budget(lead, analysis_data):
    assert score_lead(lead, quiet_analysis(analysis_data, budget_mentioned=True)).score == 0
