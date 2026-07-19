"""RAG-powered natural-language task intake.

Flow: owner free text -> retriever finds relevant care-guideline snippets ->
Gemini turns (text + snippets) into structured Task field proposals ->
proposals are validated/clamped -> caller (app.py) shows them to the owner
for approval before they become real Task objects.
"""
import json
import logging
import os
import re
from dataclasses import dataclass, field

from pawpal_system import Task
from retriever import Chunk, Retriever

logger = logging.getLogger("pawpal.ai_intake")

VALID_CATEGORIES = {"walk", "feeding", "meds", "grooming", "enrichment"}
VALID_PRIORITIES = {"high", "medium", "low"}
VALID_FREQUENCIES = {"daily", "weekly"}
MAX_DURATION_MINUTES = 60
MODEL_NAME = "gemini-flash-lite-latest"

_PROMPT_TEMPLATE = """You are a pet care scheduling assistant. An owner described a care \
task in free text for their pet. Use the reference guidelines below (retrieved \
from a pet care knowledge base) to propose reasonable task fields.

Pet species: {species}
Owner request: "{owner_text}"

Reference guidelines:
{snippets}

Return ONLY a JSON array (no markdown fences, no prose) where each item has \
exactly these fields:
- title (string, short and specific)
- category (one of: walk, feeding, meds, grooming, enrichment)
- duration_minutes (integer, 1-60)
- priority (one of: high, medium, low)
- is_recurring (boolean)
- frequency (one of: daily, weekly - only meaningful if is_recurring is true)
- reasoning (short string citing which guideline informed the duration/priority)

If the request implies multiple tasks, return multiple items. If the request \
is unsafe, unclear, or out of scope for routine pet care, return an empty array.
"""


@dataclass
class ProposedTask:
    task: Task
    reasoning: str
    warnings: list[str] = field(default_factory=list)


@dataclass
class IntakeResult:
    proposals: list[ProposedTask]
    snippets_used: list[Chunk]
    raw_response: str
    error: str | None = None


def _format_snippets(snippets: list[Chunk]) -> str:
    if not snippets:
        return "(no matching guidelines found)"
    return "\n".join(f"- [{c.source} / {c.heading}] {c.text}" for c in snippets)


def _call_gemini(prompt: str) -> str:
    """Call the Gemini API and return the raw text response. Isolated for easy mocking in tests."""
    from google import genai

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to a local .env file (see .env.example)."
        )

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    return response.text or ""


def _extract_json_array(raw: str) -> list:
    """Strip markdown code fences if present and parse the JSON array."""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE)
    match = re.search(r"\[.*\]", cleaned, flags=re.DOTALL)
    if not match:
        raise ValueError("No JSON array found in model response")
    return json.loads(match.group(0))


def _validate_item(item: dict) -> ProposedTask:
    """Validate/clamp one proposed task dict into a safe Task + warning list."""
    warnings: list[str] = []

    title = str(item.get("title") or "Untitled task").strip()[:80]

    category = item.get("category")
    if category not in VALID_CATEGORIES:
        warnings.append(f"Unknown category '{category}', defaulted to 'enrichment'")
        category = "enrichment"

    try:
        duration = int(item.get("duration_minutes"))
    except (TypeError, ValueError):
        duration = 15
        warnings.append("Missing/invalid duration, defaulted to 15 minutes")
    if duration < 1 or duration > MAX_DURATION_MINUTES:
        clamped = max(1, min(duration, MAX_DURATION_MINUTES))
        warnings.append(f"Duration {duration} out of safe range, clamped to {clamped}")
        duration = clamped

    priority = item.get("priority")
    if priority not in VALID_PRIORITIES:
        warnings.append(f"Unknown priority '{priority}', defaulted to 'medium'")
        priority = "medium"

    is_recurring = bool(item.get("is_recurring", False))

    frequency = item.get("frequency") or "daily"
    if frequency not in VALID_FREQUENCIES:
        warnings.append(f"Unknown frequency '{frequency}', defaulted to 'daily'")
        frequency = "daily"

    reasoning = str(item.get("reasoning") or "").strip()

    task = Task(
        title=title,
        category=category,
        duration_minutes=duration,
        priority=priority,
        is_recurring=is_recurring,
        frequency=frequency,
    )
    return ProposedTask(task=task, reasoning=reasoning, warnings=warnings)


def parse_tasks_from_text(
    owner_text: str,
    species: str,
    retriever: Retriever | None = None,
    llm_call=_call_gemini,
    owner_notes: str | None = None,
) -> IntakeResult:
    """Retrieve relevant guidelines, ask the LLM to propose Task fields, validate the result.

    owner_notes: optional freeform context (e.g. vet visit notes) blended into
    retrieval alongside the static knowledge/ files (see Retriever.retrieve).
    """
    retriever = retriever or Retriever()
    snippets = retriever.retrieve(owner_text, species=species, k=3, owner_notes=owner_notes)

    prompt = _PROMPT_TEMPLATE.format(
        species=species,
        owner_text=owner_text,
        snippets=_format_snippets(snippets),
    )

    try:
        raw = llm_call(prompt)
    except Exception as exc:  # noqa: BLE001 - surface any API/network failure safely
        logger.warning("Gemini call failed: %s", exc)
        return IntakeResult(proposals=[], snippets_used=snippets, raw_response="", error=str(exc))

    try:
        items = _extract_json_array(raw)
    except (ValueError, json.JSONDecodeError) as exc:
        logger.warning("Could not parse model response as JSON: %s", exc)
        return IntakeResult(proposals=[], snippets_used=snippets, raw_response=raw, error=str(exc))

    proposals = [_validate_item(item) for item in items if isinstance(item, dict)]
    return IntakeResult(proposals=proposals, snippets_used=snippets, raw_response=raw)
