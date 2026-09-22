"""Adapt Laya's typed decisions to LeadPilot's analysis schema."""

from functools import lru_cache
import math
import re

from pydantic import ValidationError

from app.schemas import LeadAnalysis, LeadInput

MODEL_NAME = "laya-router"


QUESTIONS = {
    "intent": {"type": "choice", "instructions": "What is the lead's commercial intent?",
               "criteria": {"purchase": "wants to buy, discuss, book or start a service",
                            "research": "exploring options", "support": "existing customer needs help",
                            "spam": "irrelevant promotion or malicious message",
                            "unknown": "insufficient evidence"}},
    "urgency": {"type": "choice", "instructions": "When does the lead want to start? Minggu depan means next week; bulan ini means this month.",
                "criteria": {"high": "today, this week, next week, or within two weeks",
                             "medium": "this month or soon", "low": "explicitly no urgency or far future",
                             "unknown": "no timeframe stated"}},
    "category": {"type": "choice", "instructions": "What service is requested?",
                 "criteria": {"workflow automation": "forms, Sheets, notifications, or process automation",
                              "AI integration": "AI, LLM, or chatbot integration",
                              "Python/API integration": "Python or API development",
                              "other": "a different service", "unknown": "no clear category"}},
    "service_match": {"type": "noul", "instructions": "Does this request AI or workflow automation, Python, API, or LLM integration? Forms to Google Sheets with automatic notifications counts."},
    "strong_intent": {"type": "noul", "instructions": "Does the lead explicitly want to buy, discuss, book, or start a service?"},
    "clear_requirement": {"type": "noul", "instructions": "Is a concrete problem or requirement described?"},
    "budget_mentioned": {"type": "noul", "instructions": "Is an explicit budget amount mentioned, including zero?"},
}


class LLMError(RuntimeError):
    """An analysis failure with a safe public message."""


class LLMUnavailableError(LLMError):
    pass


class LLMTimeoutError(LLMError):
    pass


class LLMOutputError(LLMError):
    pass


@lru_cache(maxsize=1)
def _router():
    from laya import Router
    return Router(max_loaded=2)


def _probability(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Expected probability")
    number = float(value)
    if not math.isfinite(number) or not 0 <= number <= 1:
        raise ValueError("Probability out of range")
    return number


def _explicit_urgency(lead: LeadInput):
    text = f"{lead.timeline} {lead.message}".lower()
    high = r"\b(hari ini|besok|minggu ini|minggu depan|today|tomorrow|this week|next week|within (one|two|2) weeks?|dalam (satu|dua|1|2) minggu)\b"
    medium = r"\b(bulan ini|this month|soon|segera)\b"
    if re.search(high, text):
        return "high"
    if re.search(medium, text):
        return "medium"
    return None


def _language_hint(lead: LeadInput):
    text = f"{lead.timeline} {lead.message}".lower()
    markers = re.findall(
        r"\b(kami|saya|ingin|untuk|dengan|tolong|minggu|bulan|bisa|mau|butuh|jasa|harga|kebutuhan|kirim|mulai)\b",
        text,
    )
    return "id" if len(markers) >= 2 else None


def analyze_lead(lead: LeadInput) -> LeadAnalysis:
    state = {"service": lead.service, "timeline": lead.timeline, "message": lead.message}
    if lead.budget is not None:
        state["budget"] = lead.budget
    try:
        hint = _language_hint(lead)
        result = _router().predict(state, QUESTIONS, **({"lang": hint} if hint else {}))
    except TimeoutError as exc:
        raise LLMTimeoutError("Laya analysis timed out.") from exc
    except (ImportError, OSError, ConnectionError) as exc:
        raise LLMUnavailableError("Laya is unavailable. Install its package and checkpoints.") from exc
    except Exception as exc:
        raise LLMUnavailableError("Laya could not analyze this lead.") from exc

    try:
        answers = result["answers"]
        choices = {key: answers[key]["choice"] for key in ("intent", "urgency", "category")}
        choices["urgency"] = _explicit_urgency(lead) or choices["urgency"]
        confidence = min(_probability(answers[key]["confidence"]) for key in choices)
        flags = {key: _probability(answers[key]["noul"]) >= 0.5 for key in
                 ("service_match", "strong_intent", "clear_requirement", "budget_mentioned")}
        flags["budget_mentioned"] = lead.budget is not None or flags["budget_mentioned"]
        summary = " ".join(lead.message.split())[:1000]
        return LeadAnalysis(**choices, **flags, summary=summary, confidence=confidence)
    except (KeyError, TypeError, ValueError, ValidationError) as exc:
        raise LLMOutputError("Laya returned invalid lead analysis.") from exc
