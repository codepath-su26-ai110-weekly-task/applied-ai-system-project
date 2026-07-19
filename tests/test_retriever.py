import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from retriever import Retriever, Chunk, load_chunks, _tokenize


def test_load_chunks_reads_real_knowledge_dir():
    chunks = load_chunks()
    assert len(chunks) > 0
    sources = {c.source for c in chunks}
    assert "dog_care.md" in sources
    assert "cat_care.md" in sources
    assert "general_safety.md" in sources


def test_tokenize_lowercases_and_drops_stopwords():
    tokens = _tokenize("The Dog needs a Bath and Medication")
    assert "the" not in tokens
    assert "and" not in tokens
    assert "dog" in tokens
    assert "bath" in tokens
    assert "medication" in tokens


def _make_test_retriever() -> Retriever:
    chunks = [
        Chunk(source="dog_care.md", heading="Medication", text="Medication is always high priority for dogs, 5 minutes."),
        Chunk(source="dog_care.md", heading="Walks", text="Walks are 20 to 30 minutes, high priority for exercise."),
        Chunk(source="cat_care.md", heading="Litter box", text="Litter box cleaning takes 10 minutes daily, medium priority."),
        Chunk(source="general_safety.md", heading="Priority defaults", text="Medication and feeding default to high priority."),
    ]
    return Retriever(chunks=chunks)


def test_retrieve_returns_relevant_chunk_first():
    retriever = _make_test_retriever()
    results = retriever.retrieve("heartworm medication for my dog", species="dog", k=2)
    assert len(results) > 0
    assert results[0].heading == "Medication"


def test_retrieve_biases_toward_requested_species():
    retriever = _make_test_retriever()
    results = retriever.retrieve("litter box cleaning", species="cat", k=1)
    assert results[0].source == "cat_care.md"


def test_retrieve_returns_only_safety_floor_for_unrelated_query():
    """An unrelated query scores 0 everywhere except the general_safety.md floor bonus."""
    retriever = _make_test_retriever()
    results = retriever.retrieve("zzz nonexistent unrelated gibberish", k=3)
    assert [c.source for c in results] == ["general_safety.md"]


def test_retrieve_respects_k_limit():
    retriever = _make_test_retriever()
    results = retriever.retrieve("priority minutes", k=1)
    assert len(results) <= 1


def test_retrieve_surfaces_owner_notes_when_relevant():
    retriever = _make_test_retriever()
    results = retriever.retrieve(
        "hypoallergenic shampoo sensitive skin",
        k=3,
        owner_notes="Vet said Biscuit has sensitive skin, use hypoallergenic shampoo.",
    )
    assert any(c.source == "owner_notes" for c in results)


def test_retrieve_ignores_blank_owner_notes():
    retriever = _make_test_retriever()
    results = retriever.retrieve("medication", k=3, owner_notes="   ")
    assert all(c.source != "owner_notes" for c in results)


def test_retrieve_without_owner_notes_unaffected():
    retriever = _make_test_retriever()
    results = retriever.retrieve("medication", k=3)
    assert all(c.source != "owner_notes" for c in results)
