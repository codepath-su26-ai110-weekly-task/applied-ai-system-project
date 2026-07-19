"""Evaluation harness for the AI Task Assistant (RAG + Gemini) pipeline.

Runs a fixed set of freeform owner requests (eval_cases.json) through the
real ai_intake.parse_tasks_from_text pipeline and checks the proposed
task fields against expectations. Prints a pass/fail summary.

Usage:
    python eval/run_eval.py
Requires GEMINI_API_KEY to be set (see .env.example).
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

from ai_intake import parse_tasks_from_text
from retriever import Retriever

load_dotenv()

CASES_PATH = os.path.join(os.path.dirname(__file__), "eval_cases.json")


def evaluate_case(case: dict, retriever: Retriever) -> tuple[bool, str]:
    result = parse_tasks_from_text(
        case["owner_text"], species=case["species"], retriever=retriever
    )

    if result.error:
        return False, f"AI call failed: {result.error}"

    if case.get("expect_empty"):
        if not result.proposals:
            return True, "correctly returned no tasks for an unsafe/unclear request"
        return False, f"expected no tasks, got {len(result.proposals)}"

    if not result.proposals:
        return False, "expected at least one task, got none"

    # A pass means at least one proposed task matches the expected category/priority/bounds.
    for proposal in result.proposals:
        t = proposal.task
        if case.get("expect_category") and t.category != case["expect_category"]:
            continue
        expected_priority = case.get("expect_priority")
        if expected_priority:
            allowed = [expected_priority] if isinstance(expected_priority, str) else expected_priority
            if t.priority not in allowed:
                continue
        if case.get("max_duration") and t.duration_minutes > case["max_duration"]:
            continue
        if "expect_recurring" in case and t.is_recurring != case["expect_recurring"]:
            continue
        if case.get("expect_frequency") and t.frequency != case["expect_frequency"]:
            continue
        return True, f"matched: {t.category}/{t.priority}/{t.duration_minutes}min"

    got = [(t.task.category, t.task.priority, t.task.duration_minutes) for t in result.proposals]
    return False, f"no proposal matched expectations; got {got}"


def main() -> None:
    if not os.environ.get("GEMINI_API_KEY"):
        print("GEMINI_API_KEY is not set. Add it to a local .env file (see .env.example).")
        sys.exit(1)

    with open(CASES_PATH, "r", encoding="utf-8") as f:
        cases = json.load(f)

    retriever = Retriever()
    passed = 0
    print(f"Running {len(cases)} eval case(s)...\n")

    for i, case in enumerate(cases):
        if i > 0:
            time.sleep(13)  # stay under the free-tier 5-requests-per-minute limit
        ok, detail = evaluate_case(case, retriever)
        status = "PASS" if ok else "FAIL"
        passed += int(ok)
        print(f"[{status}] {case['name']}: {detail}")

    print(f"\n{passed}/{len(cases)} cases passed ({passed / len(cases):.0%})")


if __name__ == "__main__":
    main()
