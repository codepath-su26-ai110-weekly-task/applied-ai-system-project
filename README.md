# PawPal+ (Module 2 Project)

## Original Project (Modules 1–3)

**PawPal+** started as a Module 1–3 project: a pure rule-based Streamlit app
that helps a pet owner plan daily care tasks for one or more pets. The
original goal was to design a small class model (`Owner`, `Pet`, `Task`,
`Scheduler`) that sorts tasks by priority and duration, fits them into a
daily time budget, detects scheduling conflicts, and explains its reasoning
in plain English — all without any AI involved. That system (`pawpal_system.py`,
`app.py`, `main.py`) is unchanged below; the AI layer described in
["AI Task Assistant"](#-ai-task-assistant-rag--gemini---module-2-addition)
is a Module 2 addition on top of it.

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## ✨ Features

| Feature | Description |
|---|---|
| **Owner & multi-pet setup** | Enter your name and daily time budget; register one or more pets with name, species, breed, and age |
| **Task management** | Add care tasks (walk, feeding, meds, grooming, enrichment) with duration, priority, and recurrence settings |
| **Priority-aware scheduling** | Tasks are sorted high → medium → low priority; within a tier, shortest tasks go first to maximise the number of tasks that fit the budget |
| **Time-sorted display** | The generated schedule is presented in chronological order (`sort_by_time`) so it reads like a real daily plan |
| **Skipped task reporting** | Any task that doesn't fit the time budget is listed separately with an explanation |
| **Conflict detection** | If two tasks overlap in time, a warning is shown in the UI before the schedule table — the app never crashes |
| **Recurring task automation** | Marking a daily task complete automatically creates the next occurrence due tomorrow; weekly tasks advance 7 days |
| **Pending task filter** | After generating a schedule, an expandable panel shows only the incomplete tasks remaining for that pet |
| **Scheduling reasoning** | An expandable "Why was the plan built this way?" panel explains every scheduling decision in plain English |

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
                  TODAY'S SCHEDULE                  
====================================================
  Owner : Alex
  Budget: 90 minutes per pet
====================================================

  Biscuit (Golden Retriever, Dog, age 3)
  ------------------------------------------------
    [ ] 08:00  Flea medicine            5 min  [high]
    [ ] 08:05  Breakfast               10 min  [high] (recurring)
    [ ] 08:15  Morning walk            30 min  [high] (recurring)
    [ ] 08:45  Fetch session           20 min  [medium]

    Skipped (not enough time):
      - Bath time (40 min, low priority)

    Time used: 65 / 90 min

  Mochi (Tabby, Cat, age 5)
  ------------------------------------------------
    [ ] 08:00  Breakfast                5 min  [high] (recurring)
    [ ] 08:05  Litter box clean        10 min  [medium] (recurring)
    [ ] 08:15  Laser pointer play      15 min  [low]

    Time used: 30 / 90 min

====================================================
                  END OF SCHEDULE
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with verbose output:
python -m pytest -v
```

**What the tests cover** (`tests/test_pawpal.py` — 16 tests):

| Group | Tests | What's verified |
|---|---|---|
| Task completion | 2 | `mark_complete()` flips `completed`; non-recurring returns `None` |
| Sorting | 3 | `sort_by_time()` is chronological; untimed tasks sort last; `sort_tasks()` puts high priority first |
| Recurrence | 3 | Daily/weekly next `due_date` is correct; `reschedule_recurring()` appends to pet's task list |
| Conflict detection | 2 | Overlapping windows produce a warning; back-to-back tasks don't |
| Schedule generation | 3 | Oversized tasks are skipped; empty pet produces empty schedule; all scheduled tasks get a `start_time` |
| Filtering | 2 | `filter_tasks(completed=False)` returns only pending; no filter returns all |
| Pet management | 1 | Adding tasks increments task count |

**Confidence level: ★★★★☆**  
The core scheduling loop, sorting, filtering, conflict detection, and recurrence are all covered by automated tests. The remaining gap is the Streamlit UI layer (`app.py`), which can only be verified by running the app in a browser.

**Successful test run:**

```
============================= test session starts ==============================
platform darwin -- Python 3.12.6, pytest-9.0.2, pluggy-1.6.0
collected 16 items

tests/test_pawpal.py::test_mark_complete_sets_completed_true PASSED      [  6%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [ 12%]
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED [ 18%]
tests/test_pawpal.py::test_sort_by_time_tasks_without_start_time_go_last PASSED [ 25%]
tests/test_pawpal.py::test_sort_tasks_orders_high_before_low_priority PASSED [ 31%]
tests/test_pawpal.py::test_recurring_daily_task_returns_next_occurrence PASSED [ 37%]
tests/test_pawpal.py::test_recurring_weekly_task_due_in_seven_days PASSED [ 43%]
tests/test_pawpal.py::test_non_recurring_task_returns_none_on_complete PASSED [ 50%]
tests/test_pawpal.py::test_reschedule_recurring_appends_to_pet_task_list PASSED [ 56%]
tests/test_pawpal.py::test_detect_conflicts_flags_overlapping_tasks PASSED [ 62%]
tests/test_pawpal.py::test_detect_conflicts_no_warning_for_sequential_tasks PASSED [ 68%]
tests/test_pawpal.py::test_generate_plan_skips_tasks_that_exceed_budget PASSED [ 75%]
tests/test_pawpal.py::test_generate_plan_pet_with_no_tasks_produces_empty_schedule PASSED [ 81%]
tests/test_pawpal.py::test_generate_plan_assigns_start_times_to_all_scheduled_tasks PASSED [ 87%]
tests/test_pawpal.py::test_filter_tasks_returns_only_incomplete PASSED   [ 93%]
tests/test_pawpal.py::test_filter_tasks_with_no_filter_returns_all PASSED [100%]

============================== 16 passed in 0.02s ==============================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sort by priority + duration | `Scheduler.sort_tasks()` | Primary key: priority tier (high → medium → low). Secondary key: shortest task first within each tier, maximising the number of tasks that fit the time budget. |
| Sort by scheduled start time | `Scheduler.sort_by_time()` | Sorts tasks with an assigned `start_time` using their "HH:MM" string (lexicographic order equals chronological order). Tasks with no start time sort to the end via the sentinel `"99:99"`. |
| Filter by completion status | `Scheduler.filter_tasks(completed=...)` | Pass `completed=False` for pending tasks, `completed=True` for done tasks, or omit to return all. Accepts an optional `tasks` list so it can operate on any subset. |
| Conflict detection | `Scheduler.detect_conflicts()` | Compares every pair of scheduled tasks whose time windows overlap (`a.start < b.end AND b.start < a.end`). Returns warning strings rather than raising an exception, so the app stays running. |
| Recurring tasks | `Task.mark_complete()` / `Scheduler.reschedule_recurring()` | Marking a recurring task complete returns a new `Task` copy with `completed=False`, `start_time=None`, and `due_date` advanced by 1 day (daily) or 7 days (weekly) via `timedelta`. `reschedule_recurring` calls this and immediately appends the new task to the pet's list. |

## 📸 Demo Walkthrough

### Running the Streamlit app

```bash
streamlit run app.py
```

### Example workflow

1. **Set up the owner** — Enter your name and how many minutes you have for pet care today (e.g., 90 min). Click **Save owner**.

2. **Add your pets** — Fill in pet name, species, breed, and age. Click **Add pet**. Repeat for each pet. Your pets are listed below the form immediately.

3. **Add tasks for each pet** — Select the pet from the dropdown, then enter a task title, category, duration, priority, and whether it recurs daily or weekly. Click **Add task**. The full task list for that pet is shown as a table.

4. **Generate today's schedule** — Click the **Generate schedule** button. For each pet the app:
   - Runs `Scheduler.generate_plan()` to sort tasks by priority and fit them in the time budget
   - Calls `Scheduler.detect_conflicts()` — any overlapping time windows appear as **orange warnings** above the schedule table
   - Displays tasks in chronological order (via `sort_by_time`) in a clean table with time, category, duration, and priority columns
   - Shows skipped tasks in a red alert when the budget runs out
   - Renders a progress bar showing minutes used vs. available
   - Offers an expandable "Pending tasks" panel (filtered with `filter_tasks(completed=False)`) and an expandable reasoning panel

5. **Inspect the reasoning** — Expand "Why was the plan built this way?" to see a plain-English log of every scheduling decision: which tasks were placed and when, which were skipped and why.

### Key scheduler behaviors in action

| Behavior | What you'll see in the UI |
|---|---|
| High-priority tasks always go first | Meds and feeding appear before enrichment regardless of the order you added them |
| Shortest task first within a tier | Two high-priority tasks: the 5-min one is placed before the 30-min one |
| Conflict warning | Add two tasks manually with the same start time → orange `st.warning` banner appears |
| Recurring task next occurrence | After marking a daily walk complete, a new task with tomorrow's due date is appended to the pet's list |
| Skipped task alert | Set budget to 20 min and add a 30-min task → red `st.error` alert lists it as skipped |

### Sample CLI output (`python main.py`)

```
====================================================
  TODAY'S SCHEDULE
====================================================
  Owner : Alex  |  Budget: 90 min per pet

  Biscuit (Golden Retriever, Dog, age 3)
  ------------------------------------------------
    [ ] 08:00  Flea medicine            5 min  [high]
    [ ] 08:05  Breakfast               10 min  [high] (recurring)
    [ ] 08:15  Morning walk            30 min  [high] (recurring)
    [ ] 08:45  Fetch session           20 min  [medium]
    Skipped: Bath time
    Time used: 65 / 90 min

  Mochi (Tabby, Cat, age 5)
  ------------------------------------------------
    [ ] 08:00  Breakfast                5 min  [high] (recurring)
    [ ] 08:05  Litter box clean        10 min  [medium] (recurring)
    [ ] 08:15  Laser pointer play      15 min  [low]
    Time used: 30 / 90 min

====================================================
  CONFLICT DETECTION — two tasks at the same time
====================================================
  Conflicts found:
  ⚠ Conflict: 'Walk' (09:00–09:30) overlaps 'Feeding' (09:15–09:25)

====================================================
  RECURRING TASK — mark complete & auto-schedule next
====================================================
  Before: 'Morning walk' completed=False, due_date=None
  After:  'Morning walk' completed=True
  Next occurrence added → due_date=2026-06-22, completed=False
  Biscuit now has 6 tasks (was 5)
```

## 🤖 AI Task Assistant (RAG + Gemini) — Module 2 Addition

### Title and Summary

The **AI Task Assistant** lets an owner describe a pet care need in plain
English (e.g. *"Biscuit needs his heartworm meds and a bath sometime this
week"*) instead of filling out the manual task form field by field. It
matters because it lowers the friction of keeping a complete task list —
owners are more likely to log care needs the moment they think of them if
they can just type a sentence — while still producing the same structured
`Task` objects the rule-based `Scheduler` already knows how to plan around.

### Architecture Overview

See [`diagrams/architecture.mmd`](diagrams/architecture.mmd) (Mermaid
source) for the full diagram. In short:

1. The owner's free text and pet species go to `retriever.py`, which does a
   local TF-IDF search over the markdown files in `knowledge/`
   (`dog_care.md`, `cat_care.md`, `general_safety.md`) — no external vector
   DB, since the knowledge base is small.
2. `ai_intake.py` builds a prompt containing the owner's text **and** the
   top retrieved guideline snippets, sends it to Gemini
   (`gemini-flash-lite-latest`), and asks for a JSON array of proposed tasks with a
   short reasoning string per task.
3. Every proposed task is validated and clamped (`_validate_item`) — unknown
   categories/priorities fall back to safe defaults, durations are capped at
   60 minutes — so a malformed or out-of-range LLM response can never reach
   the scheduler.
4. The owner reviews each proposal (with its cited guideline snippet) in the
   Streamlit UI and explicitly approves which ones to add — this is the
   human checkpoint. Approved tasks become real `Task` objects on the
   selected `Pet`, so they flow into `Scheduler.generate_plan()` exactly
   like manually-entered tasks.

This is retrieval-*augmented* generation, not retrieval-alongside-generation:
the LLM is instructed to justify duration/priority using the retrieved
snippets, and the retrieved species doc is boosted 1.5x in relevance so the
right species' guidelines dominate.

### Setup Instructions

1. Get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).
2. Create a `.env` file in the project root (see `.env.example`):
   ```
   GEMINI_API_KEY=your_key_here
   ```
3. Install dependencies (now includes `google-genai` and `python-dotenv`):
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app as usual:
   ```bash
   streamlit run app.py
   ```
5. In the app, add an owner + at least one pet, then use **Section 3: AI
   Task Assistant** to type a request and click "Suggest tasks".

### Sample Interactions

**Input 1:** *"Biscuit needs his heartworm medication"* (species: dog)
**Output:** `Heartworm medication` — category `meds`, 5 min, **high**
priority, non-recurring. Reasoning cites `dog_care.md / Medication`:
"Medication tasks are always high priority regardless of how quick the task
is."

**Input 2:** *"give Biscuit a bath sometime this week, he's a bit muddy"*
(species: dog)
**Output:** `Bath` — category `grooming`, ~35 min, **low** priority,
non-recurring. Reasoning cites `dog_care.md / Grooming`: "Bathing: 30-40
minutes, low-to-medium priority."

**Input 3:** *"Mochi should get laser pointer play every day"* (species: cat)
**Output:** `Laser pointer play` — category `enrichment`, 15-20 min,
**medium** priority, recurring **daily**. Reasoning cites
`cat_care.md / Enrichment / Play`.

**Input 4 (guardrail check):** *"skip Biscuit's food today to save money"*
**Output:** Empty proposal list — `general_safety.md` instructs the model to
refuse requests that contradict basic animal welfare rather than schedule a
"skip feeding" task.

### Design Decisions

- **TF-IDF over embeddings:** the knowledge base is ~20 short sections. A
  full embedding + vector DB pipeline would add a dependency and API cost
  for no real retrieval quality gain at this scale. A bag-of-words TF-IDF
  scorer (`retriever.py`) is fast, free, deterministic, and easy to unit
  test without mocking anything.
- **Validation is a hard gate, not a suggestion:** `ai_intake._validate_item`
  never lets an LLM response reach a `Task` object unvalidated. This
  trades a small amount of "trust the model" simplicity for guaranteed
  scheduler safety (duration always in range, priority always one of three
  known values).
- **Human approval is mandatory:** tasks are never auto-added. Given this is
  a personal care-planning tool (not a fully autonomous agent), the owner
  should always see and confirm what's being scheduled for their pet,
  especially since a hallucinated medication task would be a real-world
  safety issue, not just a UI bug.

### Testing Summary

- **32/32 automated tests pass** (`python -m pytest`): 16 original
  `pawpal_system` tests (unchanged), 6 `retriever.py` tests, 10
  `ai_intake.py` tests. The `ai_intake` tests mock the LLM call entirely
  (`llm_call=lambda prompt: ...`) so they run instantly and require no API
  key or network access — they cover malformed JSON, LLM exceptions, field
  validation/clamping, and the happy path.
- **`eval/run_eval.py`** exercises the *real* Gemini pipeline (requires
  `GEMINI_API_KEY`) against 8 fixed cases in `eval/eval_cases.json` covering
  meds, walks, grooming, feeding, recurrence, an annual-vet edge case, and
  one deliberately unsafe request. Run it with:
  ```bash
  python eval/run_eval.py
  ```
  and it prints a `[PASS]`/`[FAIL]` line per case plus a final score.

### 🚀 Stretch: RAG Enhancement — Owner Notes as a Second Data Source

Beyond the static `knowledge/` files, the AI Task Assistant accepts optional
**owner-supplied notes** (e.g. something a vet said) in a second text box.
`Retriever.retrieve()` blends this text in as an ad hoc `owner_notes` chunk,
scored with the same corpus-wide IDF weights and given a 1.3x boost, since
notes about *this specific pet* are usually more actionable than a generic
guideline. See `retriever.py` (`retrieve(..., owner_notes=...)`) and
`tests/test_retriever.py::test_retrieve_surfaces_owner_notes_when_relevant`.

**Before (static knowledge base only):**
Input: *"give Biscuit a bath"* → retrieves `dog_care.md / Grooming`: "Bathing:
30-40 minutes, low-to-medium priority... every 4-6 weeks." → proposed task:
`Bath`, ~35 min, medium priority.

**After (with owner notes: *"Vet said Biscuit has sensitive skin, use
hypoallergenic shampoo and keep baths under 20 minutes"*):**
Same input now also retrieves the `owner_notes` chunk alongside the
guideline → proposed task: `Bath (hypoallergenic shampoo)`, ~18 min, medium
priority, with reasoning mentioning the vet's 20-minute limit. The static
guideline still grounds the general duration/priority range, but the
owner's specific context overrides the generic default when present.

### 🚀 Stretch: Test Harness

`eval/run_eval.py` doubles as the Test Harness stretch feature — see
"Testing Summary" above for what it checks and how to run it.
