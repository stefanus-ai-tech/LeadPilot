# Validation status - 2026-09-20

## Laya migration - 2026-09-23

- Granite/Ollama integration was replaced with Laya typed decisions. The original
  API response shape and deterministic scoring remain.
- 92 unit tests pass with Laya mocked. `pip check` reports no broken requirements.
- Live FastAPI smoke test passes with Laya's multilingual checkpoint: the Indonesian
  sample returns purchase/high, service match, score 100, and HOT.
- Laya's router classified a mixed Indonesian/English message as English, so the
  adapter now gives clearly Indonesian messages an explicit language hint.
- The local model output on one sample does not establish general classification
  accuracy or calibrated confidence for this sales dataset.
- The notes below describe the previous Granite version and are retained as
  historical validation evidence.

Project location: `C:\Users\DELL\Documents\LocalLLM\LeadPilot\LeadPilot`.

- Created a local Python 3.11 virtual environment in `.venv` and installed all requirements. `pip check` reports no broken requirements.
- Unit tests: 84 passed. No real Ollama calls occur in the unit suite.
- Live integration: FastAPI TestClient -> normalization -> local Ollama `granite4.2:3b` -> validated analysis -> deterministic scoring passed.
- The first real model run misclassified the sample urgency and service match. Clarified the prompt with Indonesian timeframe mappings and the offered workflow automation services. The subsequent run returned purchase, high urgency, service_match=true, strong_intent=true, score 100, tier HOT.
- The smoke test now checks these semantic expectations as well as schema and scoring consistency; a regression fails the command. Successful results are saved to `smoke-result.json`.
- Recorded installed versions in `requirements-lock.txt`.

## GUI validation

- Added a FastAPI-served dashboard at `/`, with local CSS and JavaScript assets.
- The existing 84 backend tests still pass after adding the GUI routes.
- Started Uvicorn on loopback port 8001 (8000 was already occupied).
- Verified the browser form, sample selection, disabled controls during processing,
  real model submission, and rendered result: purchase/high/service match, 100/HOT,
  in 15.4 seconds. Inspected desktop and vertical-mode layouts visually.
- Added a Windows launcher and demo instructions in README.md.

## Batch CSV validation

- Generated 50 fictional leads; verified all 50 inputs pass LeadInput validation
  and all lead IDs are unique. Native file picker dependency Tk 8.6 is available.
- 98 tests pass, covering existing API logic plus CSV parsing, multiline and
  semicolon inputs, metadata preservation, per-row errors, retry, interruption,
  resume, changed-input isolation, formula escaping, folder iteration, and picker
  cancellation. Picker cancellation is mocked; native dialog appearance was not
  visually tested.
- Real-model batch results are retained in `batch_output`. Processing success
  means valid structured output, not verified semantic correctness. Spot checks
  found a logo-design request (`DUMMY-028`) incorrectly marked as a service match,
  promotional copy (`DUMMY-029`) marked unknown, and a three-month timeline
  (`DUMMY-034`) marked medium urgency. These outputs were not manually relabeled.

Known limits: model confidence is self-reported and this synthetic dataset is not
an accuracy benchmark. Review classifications before sales follow-up. The test
dependencies emit two deprecation warnings (Starlette httpx support and the AnyIO
BlockingPortal alias); these did not fail tests. No n8n is included. Mode short is
a layout option; it does not record video.
