# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Extend the original rule-based PawPal+ scheduler with a fully-integrated AI
feature (RAG), plus the required diagrams, README/model card docs, tests,
and two stretch features (a test harness and a second RAG data source) -
end to end, autonomously, across many files.

**What did the agent do?**

Scaffolded `assets/`, `diagrams/`, `knowledge/`, `eval/`; wrote
`diagrams/architecture.mmd`; wrote three knowledge-base markdown files;
built `retriever.py` (TF-IDF search) and `ai_intake.py` (Gemini call +
JSON validation/clamping) with unit tests for both (`tests/test_retriever.py`,
`tests/test_ai_intake.py`); wired a new "AI Task Assistant" section into
`app.py`; updated `requirements.txt`/`.gitignore`/added `.env.example`;
built `eval/run_eval.py` + `eval/eval_cases.json`; wrote `README.md` and
`model_card.md`; then added the owner-notes RAG enhancement (extended
`Retriever.retrieve()`, wired a second text box into `app.py`, added tests);
ran `pytest` after every major step (35 tests, all passing by the end).

**What did you have to verify or fix manually?**

Two real bugs came up during the agent's own test runs, not from separate
manual review: (1) a retriever test initially asserted an unrelated query
returns zero chunks, but the intentional `general_safety.md` relevance
floor meant one low-score chunk always surfaces - the test's expectation
was wrong, not the code, so it was corrected to match the designed
behavior. (2) after adding owner notes as a second retrieval source, a new
test failed because the TF-IDF `_idf` dict only had entries for terms seen
in the static knowledge base at construction time - any owner-note term
absent from that corpus scored an IDF of 0.0 and never surfaced. Fixed by
adding a `_default_idf` fallback (the IDF value a term would get if it
appeared in zero corpus documents) instead of silently treating unseen
terms as irrelevant. Both required understanding *why* the score was zero,
not just re-running until green - the agent traced the fallback logic in
`_score()` before proposing the fix.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
