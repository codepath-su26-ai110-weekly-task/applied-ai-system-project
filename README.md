# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

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

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
