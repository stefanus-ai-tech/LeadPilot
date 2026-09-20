from unittest.mock import Mock

import pytest

from app.schemas import LeadAnalysis, LeadInput


@pytest.fixture(autouse=True)
def block_live_ollama(monkeypatch):
    monkeypatch.setattr("app.llm.Client", Mock(side_effect=AssertionError("Unit tests must not call Ollama")))


@pytest.fixture
def lead_data():
    return {"name": "Sarah", "email": "sarah@example.com", "message": "Need AI automation please."}


@pytest.fixture
def lead(lead_data):
    return LeadInput(**lead_data)


@pytest.fixture
def analysis_data():
    return dict(intent="purchase", urgency="high", category="AI automation",
                service_match=True, strong_intent=True, clear_requirement=True,
                budget_mentioned=True, summary="Wants sales automation.", confidence=0.95)


@pytest.fixture
def analysis(analysis_data):
    return LeadAnalysis(**analysis_data)
