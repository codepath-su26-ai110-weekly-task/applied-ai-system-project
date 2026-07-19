import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ai_intake import parse_tasks_from_text, _extract_json_array, _validate_item
from retriever import Retriever, Chunk


def _fake_retriever() -> Retriever:
    return Retriever(chunks=[
        Chunk(source="dog_care.md", heading="Medication", text="Medication is high priority, 5 minutes."),
    ])


def test_extract_json_array_handles_markdown_fences():
    raw = '```json\n[{"title": "Walk"}]\n```'
    result = _extract_json_array(raw)
    assert result == [{"title": "Walk"}]


def test_extract_json_array_handles_plain_json():
    raw = '[{"title": "Walk"}]'
    assert _extract_json_array(raw) == [{"title": "Walk"}]


def test_validate_item_accepts_well_formed_input():
    item = {
        "title": "Heartworm meds", "category": "meds", "duration_minutes": 5,
        "priority": "high", "is_recurring": True, "frequency": "daily",
        "reasoning": "Guidelines say meds are always high priority.",
    }
    proposal = _validate_item(item)
    assert proposal.task.title == "Heartworm meds"
    assert proposal.task.category == "meds"
    assert proposal.warnings == []


def test_validate_item_falls_back_on_unknown_category():
    item = {"title": "Mystery task", "category": "surgery", "duration_minutes": 10, "priority": "medium"}
    proposal = _validate_item(item)
    assert proposal.task.category == "enrichment"
    assert any("category" in w for w in proposal.warnings)


def test_validate_item_clamps_out_of_range_duration():
    item = {"title": "Trip to groomer", "category": "grooming", "duration_minutes": 500, "priority": "low"}
    proposal = _validate_item(item)
    assert proposal.task.duration_minutes == 60
    assert any("clamped" in w for w in proposal.warnings)


def test_validate_item_defaults_missing_priority():
    item = {"title": "Play", "category": "enrichment", "duration_minutes": 15}
    proposal = _validate_item(item)
    assert proposal.task.priority == "medium"


def test_parse_tasks_from_text_with_mocked_llm_returns_valid_task():
    fake_response = json.dumps([{
        "title": "Heartworm medication", "category": "meds", "duration_minutes": 5,
        "priority": "high", "is_recurring": False, "frequency": "daily",
        "reasoning": "Meds are always high priority per guidelines.",
    }])

    result = parse_tasks_from_text(
        "give Biscuit his medication",
        species="dog",
        retriever=_fake_retriever(),
        llm_call=lambda prompt: fake_response,
    )

    assert result.error is None
    assert len(result.proposals) == 1
    assert result.proposals[0].task.category == "meds"
    assert len(result.snippets_used) > 0


def test_parse_tasks_from_text_handles_malformed_json_gracefully():
    result = parse_tasks_from_text(
        "give Biscuit his meds",
        species="dog",
        retriever=_fake_retriever(),
        llm_call=lambda prompt: "not valid json at all",
    )
    assert result.proposals == []
    assert result.error is not None


def test_parse_tasks_from_text_handles_llm_exception_gracefully():
    def raising_call(prompt):
        raise RuntimeError("network error")

    result = parse_tasks_from_text(
        "give Biscuit his meds",
        species="dog",
        retriever=_fake_retriever(),
        llm_call=raising_call,
    )
    assert result.proposals == []
    assert "network error" in result.error


def test_parse_tasks_from_text_empty_array_means_no_tasks():
    result = parse_tasks_from_text(
        "do something unsafe and unclear",
        species="dog",
        retriever=_fake_retriever(),
        llm_call=lambda prompt: "[]",
    )
    assert result.proposals == []
    assert result.error is None
