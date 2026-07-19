# Model Card — PawPal+ AI Task Assistant

This card documents the RAG-powered AI feature added to PawPal+ (originally a
Module 1–3 rule-based scheduler): a natural-language task intake pipeline
that retrieves pet-care guidelines and uses Gemini to propose structured
tasks. See `README.md` for setup and architecture; see `retriever.py` /
`ai_intake.py` for implementation.

## Limitations and Biases

- **Knowledge base coverage is narrow.** `knowledge/` only covers dogs and
  cats with generic care guidance. Requests for other species (rabbits,
  birds, reptiles) fall back to `general_safety.md` only, so proposed
  durations/priorities for those pets are effectively ungrounded LLM guesses.
- **Retrieval is keyword/TF-IDF based, not semantic.** A request phrased with
  vocabulary that doesn't overlap the knowledge base (e.g. "vaccine" instead
  of "vaccination") may retrieve weaker or no matching guidelines, even
  though the underlying need is covered.
- **The LLM can still misclassify.** Duration and priority clamping
  (`ai_intake._validate_item`) catches out-of-range or malformed values, but
  it cannot catch a plausible-looking but wrong classification (e.g. calling
  a bath "medium" priority when the guideline says "low").
- **Breed-specific nuance is generalized.** The guidelines give ranges (e.g.
  "20-30 min walk, more for high-energy breeds") but the retriever doesn't
  reason about a specific breed's needs beyond what's in the owner's text.

## Misuse Potential and Mitigations

- **Withholding necessary care.** A malicious or careless prompt like "skip
  feeding today" could otherwise produce a task that normalizes neglect.
  `general_safety.md` explicitly instructs the model to refuse unsafe/
  out-of-scope requests and return an empty task list; `eval_cases.json`
  includes a dedicated test case (`unsafe_request`) that checks this.
- **Unsupervised medication changes.** The assistant never has access to
  actual medication dosing information and is only prompted to schedule
  *reminders* for owner-specified meds, not to recommend medications or
  dosages itself.
- **Human-in-the-loop by design.** Every proposed task is shown with its
  reasoning and source guideline snippet and requires an explicit checkbox +
  "Add approved tasks" click in the UI — nothing is added automatically.

## What Surprised Me During Testing

Two things stood out while building and testing this:

1. The **clamping/fallback layer mattered more than expected.** Even with a
   fairly explicit JSON schema in the prompt, mocked/malformed-response tests
   (`test_parse_tasks_from_text_handles_malformed_json_gracefully`) confirmed
   that without validation, a single bad field (e.g. a typo'd priority value)
   would have silently produced an invalid `Task` object that could crash
   the scheduler downstream. Building `_validate_item` as a strict gate
   before any `Task` is constructed turned out to be the most important
   piece of the pipeline, not the prompt itself.
2. The retriever's small "safety floor" bonus for `general_safety.md`
   (`retriever.py`) meant a completely unrelated query still returns *one*
   low-relevance chunk instead of nothing. This was intentional, but writing
   the retriever test (`test_retrieve_returns_only_safety_floor_for_unrelated_query`)
   made it obvious this floor needs to stay small — a stronger floor would
   drown out genuinely relevant results for borderline queries.

## AI Collaboration

**Helpful suggestion:** When designing `ai_intake.py`, using an AI coding
assistant to separate `_call_gemini` (the actual network call) from
`parse_tasks_from_text` (the orchestration logic) made the whole module
trivially testable — every test in `test_ai_intake.py` injects a fake
`llm_call` and never touches the network. This dependency-injection pattern
wasn't something I asked for explicitly; it was suggested as the natural way
to keep tests fast and free, and it was clearly the right call.

**Flawed suggestion:** An early suggestion was to have the retriever always
return exactly `k` chunks regardless of relevance score, to "guarantee
context" for the LLM. This was rejected — always padding results with
irrelevant chunks would give the model low-quality "guidance" it might treat
as authoritative, defeating the purpose of RAG. The fix was to only return
chunks that scored above zero (`retriever.py`, `retrieve()`), so an
unrelated query correctly yields little or no retrieved context instead of
noise.
