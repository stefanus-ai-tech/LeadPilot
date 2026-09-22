"""Opt-in integration smoke test: real FastAPI pipeline and local Laya."""
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
    (Path(__file__).parent / "smoke-result.json").write_text(
        result.model_dump_json(indent=2), encoding="utf-8")
    print("PASS: FastAPI -> normalization -> local Laya -> validated analysis -> Python scoring")
    print("Review the model's classification above; one smoke test does not establish accuracy.")


if __name__ == "__main__":
    main()
