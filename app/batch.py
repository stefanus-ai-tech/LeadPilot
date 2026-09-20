"""CSV adapter, resumable sequential processing, and spreadsheet-safe exports."""
import csv
import hashlib
import io
import json
import os
from pathlib import Path
from typing import Callable

from pydantic import ValidationError

from app.excel import export_excel
from app.llm import LLMError, MODEL_NAME
from app.pipeline import triage_lead
from app.schemas import LeadInput

REQUIRED = {"name", "email", "message"}
RESULT_FIELDS = ["lp_row", "lp_status", "lp_error", "lp_intent", "lp_urgency",
                 "lp_category", "lp_service_match", "lp_summary", "lp_confidence",
                 "lp_score", "lp_tier", "lp_requires_human_review", "lp_reasons"]


def load_csv(path: Path):
    raw = path.read_bytes()
    content = raw.decode("utf-8-sig")
    try:
        dialect = csv.Sniffer().sniff(content[:65536], delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(io.StringIO(content, newline=""), dialect=dialect)
    headers = reader.fieldnames
    if not headers or len(headers) != len(set(headers)):
        raise ValueError("Header CSV kosong atau duplikat.")
    if not REQUIRED.issubset(headers):
        raise ValueError("Kolom wajib: name, email, message. Header harus huruf kecil.")
    if any(key.startswith("lp_") for key in headers):
        raise ValueError("Kolom lp_ khusus hasil. Pilih CSV input asli, bukan hasil export.")
    rows = list(reader)
    if not rows:
        raise ValueError("CSV tidak memiliki baris data.")
    return raw, headers, rows


def parse_row(row: dict) -> LeadInput:
    if None in row or any(value is None for value in row.values()):
        raise ValueError("Jumlah kolom baris tidak cocok dengan header CSV.")
    payload = {key: value for key, value in row.items() if key in LeadInput.model_fields}
    for key in ("budget", "company_size"):
        value = payload.get(key, "").strip()
        if value and (not value.isascii() or not value.isdecimal()):
            raise ValueError(f"{key} harus bilangan bulat tanpa Rp, titik, atau koma.")
        payload[key] = int(value) if value else None
    if not payload.get("source", "").strip():
        payload["source"] = "csv"
    return LeadInput.model_validate(payload)


def safe_cell(value):
    """Prevent untrusted lead/model text becoming Excel formulas."""
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def atomic_json(path: Path, value):
    temporary = path.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def export_csv(path: Path, headers, rows, state, *, errors_only=False):
    temporary = path.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers + RESULT_FIELDS)
        writer.writeheader()
        for index, row in enumerate(rows, 1):
            result = state.get(str(index), {"lp_status": "pending"})
            if errors_only and result["lp_status"] != "error":
                continue
            output = {key: row.get(key, "") for key in headers}
            output.update(result)
            output["lp_row"] = index
            writer.writerow({key: safe_cell(value) for key, value in output.items()})
    temporary.replace(path)


def process_csv(source: Path, output_root: Path, *, limit: int | None = None,
                analyze: Callable = triage_lead, report: Callable = print):
    source = source.resolve()
    raw, headers, rows = load_csv(source)
    # Invalidate old results when input, pipeline code, model or host changes.
    signature = raw + MODEL_NAME.encode() + os.getenv("OLLAMA_HOST", "local").encode()
    for filename in ("batch.py", "excel.py", "llm.py", "schemas.py", "scoring.py", "pipeline.py", "validation.py"):
        signature += (Path(__file__).parent / filename).read_bytes()
    digest = hashlib.sha256(signature).hexdigest()[:16]
    destination = output_root.resolve() / f"{source.stem}-{digest}"
    destination.mkdir(parents=True, exist_ok=True)
    lock_path = destination / "run.lock"
    try:
        lock = lock_path.open("x")
    except FileExistsError as exc:
        raise ValueError(f"Batch sedang dipakai atau berhenti paksa. Pastikan tidak ada proses aktif sebelum menghapus {lock_path}") from exc
    try:
        lock.write(str(os.getpid()))
        lock.close()
        checkpoint = destination / "checkpoint.json"
        state = json.loads(checkpoint.read_text(encoding="utf-8")) if checkpoint.exists() else {}
        report(f"FILE {source.name} | {len(rows)} lead | hasil: {destination}")
        attempted = 0
        def export():
            export_csv(destination / "results.csv", headers, rows, state)
            export_csv(destination / "errors.csv", headers, rows, state, errors_only=True)
            export_excel(destination / "results.xlsx", headers, rows, state)
        export()
        for index, row in enumerate(rows, 1):
            if state.get(str(index), {}).get("lp_status") == "ok":
                report(f"[{index}/{len(rows)}] SKIP sudah selesai")
                continue
            if limit is not None and attempted >= limit:
                break
            report(f"[{index}/{len(rows)}] Memproses...")
            try:
                result = analyze(parse_row(row))
                a, s = result.analysis, result.scoring
                value = dict(lp_status="ok", lp_error="", lp_intent=a.intent,
                             lp_urgency=a.urgency, lp_category=a.category,
                             lp_service_match=a.service_match, lp_summary=a.summary,
                             lp_confidence=a.confidence, lp_score=s.score, lp_tier=s.tier,
                             lp_requires_human_review=s.requires_human_review,
                             lp_reasons="; ".join(s.reasons))
            except ValidationError as exc:
                issues = [f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in exc.errors()]
                value = dict(lp_status="error", lp_error="; ".join(issues))
            except (ValueError, LLMError) as exc:
                value = dict(lp_status="error", lp_error=str(exc))
            state[str(index)] = value
            atomic_json(checkpoint, state)
            export()
            attempted += 1
            report(f"[{index}/{len(rows)}] {value['lp_status'].upper()} "
                   f"{value.get('lp_tier', '')} {value.get('lp_score', '')}")
        counts = {key: sum(item["lp_status"] == key for item in state.values()) for key in ("ok", "error")}
        counts["pending"] = len(rows) - sum(counts.values())
        report(f"Selesai: {counts['ok']} OK / {counts['error']} error / {counts['pending']} pending")
        return destination, counts
    finally:
        lock.close()
        lock_path.unlink(missing_ok=True)
