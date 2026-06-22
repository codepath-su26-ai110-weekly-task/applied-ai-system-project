# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The three core actions a user should be able to perform in PawPal+ are:

1. **Enter owner and pet information** The user provides basic details about themselves and their pet (name, species, breed, etc.). This context anchors every scheduling decision, since constraints like walk duration or feeding frequency depend on the specific animal.

2. **Add and edit care tasks** The user can create tasks such as walks, feedings, medication reminders, grooming sessions, and enrichment activities. Each task carries at minimum a duration and a priority level so the scheduler has enough information to reason about tradeoffs when time is limited.

3. **Generate and view a daily care plan** The user requests a schedule for the day. The system orders and fits tasks within the available time window, explains why it chose that arrangement (e.g., which high-priority items came first, which low-priority items were deferred), and presents the result in a clear timeline format.

The initial design has five classes:

- **Pet** (dataclass) — holds static facts about the animal: name, species, breed, and age. It has no scheduling knowledge; it purely describes who is being cared for.
- **Task** (dataclass) — represents a single care activity with a title, category, duration, and priority. It also tracks whether it recurs and how often. The scheduler stamps a `start_time` on it when building a plan.
- **Owner** — holds the person's name, how many minutes they have available each day, any scheduling preferences, and a list of their pets. It is the source of the time budget the scheduler works within.
- **Scheduler** — the core logic class. It takes an owner, a pet, and a list of tasks. It sorts tasks by priority, fits them into the available time window, stamps each with a start time, and stores the result as `scheduled_tasks`, `skipped_tasks`, and a `reasoning` string directly on itself — no separate output object needed.

**b. Design changes**

Yes, changes were made after reviewing the skeleton against the UML and the README sample output:

1. **Added `start_time` to `Task`** — The README shows output like `08:00 — Morning walk (30 min)`, which requires a timestamp per task. The original design had no field for this. Rather than introduce a separate `ScheduledEntry` wrapper class (unnecessary complexity), `start_time: Optional[str]` was added directly to the `Task` dataclass. The scheduler sets it when building a plan; it stays `None` for unscheduled tasks.

2. **Added `pets: list[Pet]` and `add_pet()` to `Owner`** — The UML explicitly showed a 1-to-many relationship between `Owner` and `Pet`, but the original `Owner` class had no way to hold that list. This was a missing relationship caught during review.

3. **Made `sort_tasks` accept an optional `tasks` parameter** — The original signature `sort_tasks(self)` always operated on `self.tasks`. During `generate_plan`, the scheduler may need to sort a filtered subset (e.g., only recurring tasks, or only tasks under 30 minutes). Accepting `tasks: Optional[list[Task]] = None` lets the method default to `self.tasks` but remain reusable mid-plan without a bottleneck.

4. **Removed `DailyPlan`** — The project description defines exactly four classes (Task, Pet, Owner, Scheduler). `DailyPlan` was originally added as a return-value container for `generate_plan()`, but its only data (`scheduled_tasks`, `skipped_tasks`, `reasoning`) fits naturally as instance attributes on `Scheduler` itself. Removing it reduces a layer of indirection with no loss of functionality, since PawPal+ only ever shows one plan at a time.

5. **Added `completed` to `Task`** — The project description explicitly lists "completion status" as a required field. This was missing from the skeleton and was added as `completed: bool = False`.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers two constraints: **time budget** (the owner's total available minutes per day) and **task priority** (high / medium / low). Within a priority tier, tasks are ordered shortest-first so the maximum number of tasks can fit before the budget runs out.

Time was chosen as the primary hard constraint because it is the only truly fixed resource — an owner cannot create more minutes in the day. Priority is the secondary constraint because not all tasks are equally urgent (flea medicine cannot be skipped the way a play session can). Owner preferences (e.g., preferred walk times) are stored on the `Owner` object but are not yet used by the scheduler — they are the natural next constraint to add.

**b. Tradeoffs**

The conflict detector checks only for **exact time-window overlaps** between tasks that already have a `start_time` assigned. It does not account for travel time between tasks, preparation time, or "soft" conflicts like scheduling a long walk immediately before feeding (which a thoughtful owner might space out).

This tradeoff is reasonable for this scenario because PawPal+ is a personal planning tool for a single household. The owner is already present for all tasks, so travel time is zero and the main risk is actual time overlap, not logistical sequencing. Detecting exact overlaps catches the most common mistake (accidentally assigning two tasks the same slot) without requiring the scheduler to know anything about the physical layout of the owner's home or routine.

---

## 3. AI Collaboration

**a. How you used AI**

AI was used across every phase, but in different modes depending on the task:

- **Design brainstorming (Phase 1):** Asking "what classes does a pet care scheduler need?" generated a solid starting list fast. The most effective prompts were specific and constrained — "suggest classes for a scheduler that tracks time, priority, and recurrence" produced tighter output than open-ended questions. Vague prompts like "help me design a scheduler app" produced bloated designs that needed heavy trimming.
- **Code generation (Phases 2–3):** Agent/edit mode was most effective for generating class skeletons and method stubs. Asking for stubs with `pass` bodies (rather than full implementations) let me review the interface before committing to any logic, which caught the missing `pets` list on `Owner` before any code was written.
- **Algorithm implementation (Phase 3):** Chat mode worked well for targeted questions like "how do I sort HH:MM strings with a lambda key?" and "what is the interval-overlap condition for two tasks?" These short, precise questions produced correct, readable answers that could be dropped into the code with minimal editing.
- **Test planning (Phase 4):** Asking "what edge cases should I test for a scheduler with recurring tasks and conflict detection?" produced a useful checklist (empty pet, task exceeds budget, back-to-back vs. overlapping times, non-recurring tasks returning `None`). Every item on that list became a test.
- **Refactoring:** After the implementation was working, asking "how could this method be simplified?" on `_build_reasoning` produced a cleaner `header + "\n".join(reasons)` pattern that replaced a messier loop.

**b. Judgment and verification**

The clearest moment of rejection was the AI's initial suggestion to keep `DailyPlan` as a separate class. The suggestion was architecturally coherent — a dedicated output object is a common pattern — but it added a layer of indirection that served no real purpose here, since PawPal+ only ever displays one plan at a time. The `scheduled_tasks`, `skipped_tasks`, and `reasoning` data fit naturally as instance attributes on `Scheduler` itself, and removing `DailyPlan` made every method simpler to read and test.

The evaluation process was: (1) ask whether the suggested class carried any logic or just held data, (2) check whether the data could live somewhere that already existed, and (3) verify that the simplified version passed the same tests. It did — which confirmed the class was unnecessary indirection rather than genuine separation of concerns.

Keeping separate chat sessions per phase helped enforce this discipline. A fresh session for testing meant the AI had no accumulated context about the implementation choices, so its test suggestions were genuinely independent rather than confirming what had already been built. A fresh session for UML review meant the diagram critique was based on the code, not on earlier design conversations that had already been resolved.

---

## 4. Testing and Verification

**a. What you tested**

The 16-test suite covers seven behavior groups:

- **Task completion** — `mark_complete()` flips `completed` to `True`; a non-recurring task returns `None` rather than a next occurrence. These tests guard the most fundamental piece of state in the system.
- **Sorting** — `sort_by_time()` produces chronological order; untimed tasks sort last; `sort_tasks()` places high-priority tasks before low-priority ones. Without these tests, a subtle key error in the lambda could silently produce a wrong order that looks plausible at a glance.
- **Recurrence** — Daily tasks advance `due_date` by exactly 1 day; weekly tasks advance by 7; `reschedule_recurring()` appends the new task to the pet's list. This is the most stateful logic in the system — a wrong `timedelta` would corrupt every future plan.
- **Conflict detection** — Overlapping windows produce a warning string; back-to-back tasks (where one ends exactly when the next starts) do not. The boundary case is critical: off-by-one errors in the interval comparison would either miss real conflicts or flag false ones.
- **Schedule generation** — Oversized tasks are moved to `skipped_tasks`; an empty pet produces an empty schedule; every scheduled task receives a `start_time`. These tests verify the core loop's behavior at the budget boundary and with degenerate input.
- **Filtering** — `filter_tasks(completed=False)` returns only pending tasks; no filter argument returns all. These tests protect the UI from showing stale completed tasks as pending.

**b. Confidence**

**★★★★☆** — The scheduling loop, sorting, filtering, recurrence, and conflict detection are all covered by automated tests that run in under a second. The system handles the documented edge cases (empty pet, budget exceeded, back-to-back tasks, non-recurring tasks) correctly.

The remaining gap is integration-level behavior that pytest cannot easily reach: the Streamlit session state persistence across reruns, the conflict warning banner appearing in the right position in the UI, and multi-pet schedules rendering correctly. These would require browser-based UI testing (e.g., Playwright) to cover properly.

Edge cases to test next with more time:
- An owner with zero available minutes (budget fully exhausted before any task runs)
- A task whose `duration_minutes` equals exactly the remaining budget (boundary condition)
- Adding the same pet name twice through the Streamlit form and verifying the duplicate guard works
- A recurring task where `frequency` is an unexpected string (neither "daily" nor "weekly")

---

## 5. Reflection

**a. What went well**

The separation between the logic layer (`pawpal_system.py`) and the UI layer (`app.py`) worked cleanly. Because all scheduling decisions live in `Scheduler` and the UI only calls methods and reads results, it was straightforward to add conflict detection and filtering to the Streamlit app without touching any logic code. The 16-test suite also validated the backend independently, which meant that when the UI was wired up, the only remaining unknowns were Streamlit-specific rendering details — not bugs in the algorithm.

The decision to keep the design at exactly four classes (Task, Pet, Owner, Scheduler) also paid off. Removing `DailyPlan` and folding its state into `Scheduler` kept every method short, every test focused, and the overall codebase readable end-to-end in a single sitting.

**b. What you would improve**

The `Owner.preferences` dictionary is stored but never read by the Scheduler. In a next iteration, preferences would drive real scheduling decisions — for example, a "no tasks before 9am" preference would shift the `DEFAULT_START_HOUR`, or a "walk always before feeding" preference would add ordering constraints within the same priority tier. Wiring preferences into the scheduling loop is the highest-value improvement available without redesigning the class structure.

I would also split `Scheduler.generate_plan()` into smaller private methods. The current method handles sorting, time tracking, start-time assignment, and reasoning in one loop. Extracting a `_assign_start_times()` helper would make it easier to test time assignment in isolation and would make the flow of `generate_plan()` readable at a glance.

**c. Key takeaway**

The most important lesson from this project is that **AI makes you a faster drafter but not a better architect — that part is still your job.** The AI generated class skeletons, method stubs, lambda sort keys, and test cases quickly and correctly. But it could not decide whether `DailyPlan` was necessary, whether conflict detection should crash or warn, or whether the four-class limit was a constraint worth respecting. Those decisions required understanding the project's scope, the user's actual need, and the long-term cost of complexity — none of which the AI had access to.

Using AI effectively on this project meant staying in the role of lead architect: setting the design constraints first, using AI to accelerate execution within those constraints, and critically evaluating every suggestion against the design before accepting it. The sessions where that discipline held produced clean, testable code. The sessions where it slipped — accepting a suggestion without checking whether it fit the design — produced the extra class and the unused preferences field that had to be cleaned up later.
