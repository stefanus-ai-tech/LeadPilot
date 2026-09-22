from unittest.mock import Mock

import pytest

from app.llm import analyze_lead, LLMOutputError, LLMTimeoutError, LLMUnavailableError, QUESTIONS


def response(**changes):
    answers = {
        "intent": {"choice": "purchase", "confidence": 0.92},
        "urgency": {"choice": "high", "confidence": 0.84},
        "category": {"choice": "workflow automation", "confidence": 0.88},
        "service_match": {"noul": 0.9},
        "strong_intent": {"noul": 0.8},
        "clear_requirement": {"noul": 0.7},
        "budget_mentioned": {"noul": 0.2},
    }
    answers.update(changes)
    return {"answers": answers}


def test_laya_decisions_map_to_analysis(monkeypatch, lead):
    router = Mock()
    router.predict.return_value = response()
    monkeypatch.setattr("app.llm._router", Mock(return_value=router))
    result = analyze_lead(lead)
    state, questions = router.predict.call_args.args
    assert state == {"service": "", "timeline": "", "message": lead.message}
    assert questions == QUESTIONS
    assert result.intent == "purchase"
    assert result.urgency == "high"
    assert result.service_match is True
    assert result.budget_mentioned is False
    assert result.summary == lead.message
    assert result.confidence == 0.84


def test_explicit_zero_budget_counts(monkeypatch, lead):
    router = Mock()
    router.predict.return_value = response()
    monkeypatch.setattr("app.llm._router", Mock(return_value=router))
    result = analyze_lead(lead.model_copy(update={"budget": 0}))
    assert result.budget_mentioned is True
    assert router.predict.call_args.args[0]["budget"] == 0


def test_explicit_indonesian_timeframe_overrides_model(monkeypatch, lead):
    router = Mock()
    router.predict.return_value = response(urgency={"choice": "medium", "confidence": 0.8})
    monkeypatch.setattr("app.llm._router", Mock(return_value=router))
    assert analyze_lead(lead.model_copy(update={"timeline": "Minggu depan"})).urgency == "high"


def test_indonesian_lead_uses_multilingual_checkpoint(monkeypatch, lead):
    router = Mock()
    router.predict.return_value = response()
    monkeypatch.setattr("app.llm._router", Mock(return_value=router))
    analyze_lead(lead.model_copy(update={"message": "Kami ingin membeli jasa automation."}))
    assert router.predict.call_args.kwargs == {"lang": "id"}


@pytest.mark.parametrize("change", [
    {"intent": {"choice": "buy", "confidence": 0.9}},
    {"intent": {"choice": "purchase", "confidence": float("nan")}},
    {"intent": {"choice": "purchase", "confidence": 1.2}},
    {"service_match": {"noul": "true"}},
    {"urgency": {}},
])
def test_bad_decision_is_rejected(monkeypatch, lead, change):
    router = Mock()
    router.predict.return_value = response(**change)
    monkeypatch.setattr("app.llm._router", Mock(return_value=router))
    with pytest.raises(LLMOutputError):
        analyze_lead(lead)


@pytest.mark.parametrize("error,expected", [
    (ImportError("private"), LLMUnavailableError),
    (OSError("private"), LLMUnavailableError),
    (TimeoutError("private"), LLMTimeoutError),
])
def test_safe_upstream_errors(monkeypatch, lead, error, expected):
    monkeypatch.setattr("app.llm._router", Mock(side_effect=error))
    with pytest.raises(expected) as raised:
        analyze_lead(lead)
    assert "private" not in str(raised.value)
