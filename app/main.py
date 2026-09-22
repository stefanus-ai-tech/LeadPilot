from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.llm import LLMOutputError, LLMTimeoutError, LLMUnavailableError
from app.pipeline import triage_lead
from app.schemas import LeadInput, TriageResult

app = FastAPI(title="LeadPilot", version="0.1.0")
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    """Application liveness only; does not load or query Laya."""
    return {"status": "ok"}


@app.post("/triage", response_model=TriageResult)
def triage(lead: LeadInput) -> TriageResult:
    try:
        return triage_lead(lead)
    except LLMTimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except LLMUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except LLMOutputError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
