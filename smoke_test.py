"""Opt-in integration smoke test: real FastAPI pipeline and local Ollama."""
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.schemas import TriageResult
from app.scoring import score_lead


def main():
    payload = json.loads((Path(__file__).parent / "samples" / "hot-lead.json").read_text(encoding="utf-8"))
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}
        response = client.post("/triage", json=payload)
    if response.status_code != 200:
        raise SystemExit(f"Smoke test failed: HTTP {response.status_code}: {response.text}")
    result = TriageResult.model_validate(response.json())
    assert result.scoring == score_lead(result.lead, result.analysis)
    print(result.model_dump_json(indent=2))
    expected = {"intent": "purchase", "urgency": "high", "service_match": True,
                "strong_intent": True}
    mismatches = {key: {"expected": value, "actual": getattr(result.analysis, key)}
                  for key, value in expected.items() if getattr(result.analysis, key) != value}
    if mismatches or result.scoring.score != 100 or result.scoring.tier != "HOT":
        raise SystemExit(f"Smoke test failed: sample classification regression: {mismatches}; "
                         f"score={result.scoring.score}, tier={result.scoring.tier}")
    (Path(__file__).parent / "smoke-result.json").write_text(
        result.model_dump_json(indent=2), encoding="utf-8")
    print("PASS: FastAPI -> normalization -> local Ollama -> validated analysis -> Python scoring")
    print("Review the model's classification above; one smoke test does not establish accuracy.")


if __name__ == "__main__":
    main()
