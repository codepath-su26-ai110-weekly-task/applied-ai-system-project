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

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
