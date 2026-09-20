import json
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest
from ollama import ResponseError

from app.llm import analyze_lead, LLMOutputError, LLMTimeoutError, LLMUnavailableError
from app.schemas import LeadAnalysis


def mock_client(monkeypatch, *, content=None, error=None):
    client = Mock()
    client.chat.side_effect = error
    client.chat.return_value = SimpleNamespace(message=SimpleNamespace(content=content))
    factory = Mock(return_value=client)
    monkeypatch.setattr("app.llm.Client", factory)
    return factory, client


def test_structured_request_and_parsing(monkeypatch, lead, analysis_data):
    monkeypatch.setenv("OLLAMA_HOST", "http://localhost:11434")
    monkeypatch.setenv("OLLAMA_TIMEOUT_SECONDS", "45")
    factory, client = mock_client(monkeypatch, content=json.dumps(analysis_data))
    result = analyze_lead(lead)
    assert result == LeadAnalysis(**analysis_data)
    factory.assert_called_once_with(host="http://localhost:11434", timeout=45.0)
    args = client.chat.call_args.kwargs
    assert args["model"] == "granite4.2:3b"
    assert args["format"] == LeadAnalysis.model_json_schema()
    assert args["options"]["temperature"] == 0
    assert args["think"] is False
    assert args["stream"] is False
    assert json.loads(args["messages"][1]["content"].split("\n", 1)[1]) == lead.model_dump()


@pytest.mark.parametrize("content", ["not json", "", None, "{}", '```json\n{}\n```', "[]"])
def test_malformed_output(monkeypatch, lead, content):
    mock_client(monkeypatch, content=content)
    with pytest.raises(LLMOutputError):
        analyze_lead(lead)


@pytest.mark.parametrize("change", [{"confidence": 1.1}, {"confidence": -0.1}, {"confidence": float("nan")},
    {"intent": "buy"}, {"urgency": "urgent"}, {"service_match": "false"},
    {"summary": "  "}, {"score": 100}])
def test_invalid_schema(monkeypatch, lead, analysis_data, change):
    mock_client(monkeypatch, content=json.dumps(analysis_data | change))
    with pytest.raises(LLMOutputError):
        analyze_lead(lead)


@pytest.mark.parametrize("error,expected", [
    (httpx.ReadTimeout("private text"), LLMTimeoutError),
    (httpx.ConnectError("private text"), LLMUnavailableError),
    (ConnectionError("private text"), LLMUnavailableError),
    (ResponseError("private text", status_code=404), LLMUnavailableError),
])
def test_upstream_errors(monkeypatch, lead, error, expected):
    mock_client(monkeypatch, error=error)
    with pytest.raises(expected) as raised:
        analyze_lead(lead)
    assert "private text" not in str(raised.value)
