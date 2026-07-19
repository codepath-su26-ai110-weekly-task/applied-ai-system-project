"""Lightweight TF-IDF retrieval over the local knowledge/ markdown files.

No external dependencies (no embeddings, no vector DB) - the knowledge base
is small enough that a simple bag-of-words TF-IDF scorer over per-section
chunks is sufficient and keeps the whole pipeline free to run.
"""
import math
import os
import re
from collections import Counter
from dataclasses import dataclass

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "knowledge")

_STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "to", "in", "on", "is", "are",
    "for", "with", "as", "this", "that", "it", "be", "should", "not",
}


@dataclass
class Chunk:
    source: str    # e.g. "dog_care.md"
    heading: str   # e.g. "Medication"
    text: str


def _tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-z']+", text.lower())
    return [w for w in words if w not in _STOPWORDS and len(w) > 1]


def load_chunks(knowledge_dir: str = KNOWLEDGE_DIR) -> list[Chunk]:
    """Split every markdown file in knowledge_dir into ## -level section chunks."""
    chunks: list[Chunk] = []
    if not os.path.isdir(knowledge_dir):
        return chunks

    for filename in sorted(os.listdir(knowledge_dir)):
        if not filename.endswith(".md"):
            continue
        path = os.path.join(knowledge_dir, filename)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        sections = re.split(r"^## ", content, flags=re.MULTILINE)
        for section in sections[1:]:  # sections[0] is the H1 title, skip it
            lines = section.strip().splitlines()
            heading = lines[0].strip() if lines else ""
            body = "\n".join(lines[1:]).strip()
            if body:
                chunks.append(Chunk(source=filename, heading=heading, text=body))
    return chunks


class Retriever:
    """TF-IDF retriever built once over all chunks in the knowledge base."""

    def __init__(self, chunks: list[Chunk] | None = None):
        self.chunks = chunks if chunks is not None else load_chunks()
        self._doc_tokens = [_tokenize(c.text) for c in self.chunks]
        self._idf = self._build_idf(self._doc_tokens)

    def _build_idf(self, doc_tokens: list[list[str]]) -> dict[str, float]:
        n_docs = len(doc_tokens)
        self._default_idf = math.log(n_docs + 1) + 1.0  # idf for a term absent from every doc (freq=0)
        doc_freq: Counter = Counter()
        for tokens in doc_tokens:
            for term in set(tokens):
                doc_freq[term] += 1
        return {
            term: math.log((n_docs + 1) / (freq + 1)) + 1.0
            for term, freq in doc_freq.items()
        }

    def _score(self, query_tokens: list[str], doc_tokens: list[str]) -> float:
        if not doc_tokens:
            return 0.0
        doc_counts = Counter(doc_tokens)
        score = 0.0
        for term in query_tokens:
            tf = doc_counts.get(term, 0) / len(doc_tokens)
            idf = self._idf.get(term, self._default_idf)
            score += tf * idf
        return score

    def retrieve(
        self,
        query: str,
        species: str | None = None,
        k: int = 3,
        owner_notes: str | None = None,
    ) -> list[Chunk]:
        """Return the top-k most relevant chunks for query, optionally biased to a species file.

        owner_notes: optional freeform text (e.g. a vet visit note) treated as a
        second, session-scoped data source alongside the static knowledge/ files.
        It's scored with the same corpus-wide IDF weights and given a small
        relevance boost, since owner-supplied context is often more specific
        to the actual pet than the generic guideline docs.
        """
        query_tokens = _tokenize(query)
        if species:
            species_file = f"{species.lower()}_care.md"
        else:
            species_file = None

        candidates: list[tuple[list[str], Chunk]] = list(zip(self._doc_tokens, self.chunks))
        if owner_notes and owner_notes.strip():
            notes_chunk = Chunk(source="owner_notes", heading="Owner-supplied notes", text=owner_notes.strip())
            candidates.append((_tokenize(owner_notes), notes_chunk))

        scored: list[tuple[float, Chunk]] = []
        for tokens, chunk in candidates:
            score = self._score(query_tokens, tokens)
            if species_file and chunk.source == species_file:
                score *= 1.5  # bias toward the requested pet's species doc
            if chunk.source == "general_safety.md":
                score += 0.01  # tiny floor so safety notes can still surface
            if chunk.source == "owner_notes":
                score *= 1.3  # owner-supplied context is often more specific than generic docs
            scored.append((score, chunk))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [chunk for score, chunk in scored[:k] if score > 0]
