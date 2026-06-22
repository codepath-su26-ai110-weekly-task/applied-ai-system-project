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
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
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
