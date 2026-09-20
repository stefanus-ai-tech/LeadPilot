from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.llm import LLMOutputError, LLMTimeoutError, LLMUnavailableError
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_health_without_ollama(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_triage_pipeline(client, monkeypatch, lead_data, analysis):
    analyze = Mock(return_value=analysis)
    monkeypatch.setattr("app.pipeline.analyze_lead", analyze)
    response = client.post("/triage", json=lead_data | dict(name=" Sarah ", email=" SARAH@EXAMPLE.COM ",
                                                         company_size=45, budget=5_000_000))
    assert response.status_code == 200
    result = response.json()
    assert result["lead"]["name"] == "Sarah"
    assert result["lead"]["email"] == "sarah@example.com"
    assert result["analysis"] == analysis.model_dump()
    assert result["scoring"]["score"] == 100
    assert result["scoring"]["tier"] == "HOT"
    analyze.assert_called_once()
    assert analyze.call_args.args[0].email == "sarah@example.com"


@pytest.mark.parametrize("change", [{"email": "bad"}, {"name": "   "}, {"message": "  hi "},
    {"budget": -1}, {"company_size": 0}, {"budget": True}])
def test_invalid_input_never_calls_llm(client, monkeypatch, lead_data, change):
    analyze = Mock()
    monkeypatch.setattr("app.pipeline.analyze_lead", analyze)
    assert client.post("/triage", json=lead_data | change).status_code == 422
    analyze.assert_not_called()


def test_missing_fields_and_malformed_json(client):
    assert client.post("/triage", json={}).status_code == 422
    assert client.post("/triage", content="{", headers={"Content-Type": "application/json"}).status_code == 422


@pytest.mark.parametrize("error,status", [(LLMOutputError("Invalid analysis"), 502),
    (LLMTimeoutError("Analysis timed out"), 504), (LLMUnavailableError("Ollama unavailable"), 503)])
def test_upstream_error_responses(client, monkeypatch, lead_data, error, status):
    monkeypatch.setattr("app.pipeline.analyze_lead", Mock(side_effect=error))
    response = client.post("/triage", json=lead_data)
    assert response.status_code == status
    assert response.json() == {"detail": str(error)}
