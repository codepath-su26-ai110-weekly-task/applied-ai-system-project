import dataclasses
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
DEFAULT_START_HOUR = 8  # plans begin at 08:00


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

def _to_minutes(time_str: str) -> int:
    """Convert a 'HH:MM' string to total minutes since midnight."""
    h, m = time_str.split(":")
    return int(h) * 60 + int(m)


def _from_minutes(total: int) -> str:
    """Convert total minutes since midnight back to 'HH:MM' string."""
    return f"{total // 60:02d}:{total % 60:02d}"


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    title: str
    category: str              # walk | feeding | meds | grooming | enrichment
    duration_minutes: int
    priority: str              # high | medium | low
    is_recurring: bool = False
    frequency: str = "daily"   # daily | weekly
    start_time: Optional[str] = None  # set by Scheduler when building a plan, e.g. "08:00"
    completed: bool = False
    due_date: Optional[str] = None    # ISO date string "YYYY-MM-DD"

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task done; return a new Task for the next occurrence if recurring."""
        self.completed = True
        if not self.is_recurring:
            return None
        delta = timedelta(days=1) if self.frequency == "daily" else timedelta(weeks=1)
        next_due = (date.today() + delta).isoformat()
        return dataclasses.replace(self, completed=False, start_time=None, due_date=next_due)

    def is_high_priority(self) -> bool:
        """Return True if the task's priority is high."""
        return self.priority == "high"

    def to_dict(self) -> dict:
        """Serialize the task to a plain dictionary."""
        return {
            "title": self.title,
            "category": self.category,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "is_recurring": self.is_recurring,
            "frequency": self.frequency,
            "start_time": self.start_time,
            "completed": self.completed,
            "due_date": self.due_date,
        }


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> bool:
        """Remove the first task matching the given title; return True if found."""
        for i, task in enumerate(self.tasks):
            if task.title == title:
                self.tasks.pop(i)
                return True
        return False

    def get_tasks(self) -> list:
        """Return the pet's full list of tasks."""
        return self.tasks

    def get_info(self) -> str:
        """Return a formatted one-line description of the pet."""
        return f"{self.name} ({self.breed}, {self.species}, age {self.age})"

    def summary(self) -> str:
        """Return the pet's name and total task count."""
        return f"{self.name} — {len(self.tasks)} task(s)"


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    def __init__(self, name: str, available_minutes: int, preferences: Optional[dict] = None):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences: dict = preferences or {}
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_available_time(self) -> int:
        """Return the owner's daily time budget in minutes."""
        return self.available_minutes

    def update_preferences(self, prefs: dict) -> None:
        """Merge new preference keys into the owner's existing preferences."""
        self.preferences.update(prefs)

    def get_all_tasks(self) -> list:
        """Return a flat list of every task across all of the owner's pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, tasks: list):
        self.owner = owner
        self.pet = pet
        self.tasks = tasks
        self.available_minutes = owner.available_minutes
        self.scheduled_tasks: list[Task] = []
        self.skipped_tasks: list[Task] = []
        self.reasoning: str = ""

    # --- Core plan generation ---

    def generate_plan(self) -> None:
        """Build the daily schedule, populating scheduled_tasks, skipped_tasks, and reasoning."""
        self.scheduled_tasks = []
        self.skipped_tasks = []
        reasons: list[str] = []

        sorted_tasks = self.sort_tasks()
        remaining = self.available_minutes
        current = DEFAULT_START_HOUR * 60  # track time as total minutes since midnight

        for task in sorted_tasks:
            if task.duration_minutes <= remaining:
                task.start_time = _from_minutes(current)
                self.scheduled_tasks.append(task)
                remaining -= task.duration_minutes
                current += task.duration_minutes
                reasons.append(
                    f"  - {task.title} ({task.priority} priority) → {task.start_time}"
                )
            else:
                self.skipped_tasks.append(task)
                reasons.append(
                    f"  - {task.title} skipped (needs {task.duration_minutes} min, only {remaining} min left)"
                )

        self.reasoning = self._build_reasoning(reasons)

    # --- Sorting ---

    def sort_tasks(self, tasks: Optional[list] = None) -> list:
        """Sort tasks by priority (high first), then by duration ascending within each tier."""
        source = tasks if tasks is not None else self.tasks
        return sorted(source, key=lambda t: (PRIORITY_ORDER.get(t.priority, 99), t.duration_minutes))

    def sort_by_time(self, tasks: Optional[list] = None) -> list:
        """Sort tasks by start_time (HH:MM); tasks with no start_time sort to the end."""
        source = tasks if tasks is not None else self.scheduled_tasks
        return sorted(source, key=lambda t: t.start_time or "99:99")

    # --- Filtering ---

    def filter_tasks(self, tasks: Optional[list] = None, completed: Optional[bool] = None) -> list:
        """Return tasks matching the given completion status; pass None to skip that filter."""
        source = tasks if tasks is not None else self.tasks
        if completed is not None:
            source = [t for t in source if t.completed == completed]
        return source

    # --- Conflict detection ---

    def detect_conflicts(self) -> list[str]:
        """Return warning strings for any scheduled tasks whose time windows overlap."""
        warnings = []
        timed = [t for t in self.scheduled_tasks if t.start_time]
        for i, a in enumerate(timed):
            a_start = _to_minutes(a.start_time)
            a_end = a_start + a.duration_minutes
            for b in timed[i + 1:]:
                b_start = _to_minutes(b.start_time)
                b_end = b_start + b.duration_minutes
                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f"  ⚠ Conflict: '{a.title}' ({a.start_time}–{_from_minutes(a_end)}) "
                        f"overlaps '{b.title}' ({b.start_time}–{_from_minutes(b_end)})"
                    )
        return warnings

    # --- Recurring task helper ---

    def reschedule_recurring(self, task: Task) -> Optional[Task]:
        """Mark a task complete and, if recurring, add its next occurrence to this pet's task list."""
        next_task = task.mark_complete()
        if next_task:
            self.pet.add_task(next_task)
        return next_task

    # --- Display ---

    def _build_reasoning(self, reasons: list[str]) -> str:
        """Compose the human-readable reasoning string from a list of per-task decision notes."""
        total_scheduled = sum(t.duration_minutes for t in self.scheduled_tasks)
        header = (
            f"Plan for {self.pet.name} | "
            f"Budget: {self.owner.available_minutes} min | "
            f"Used: {total_scheduled} min | "
            f"Scheduled: {len(self.scheduled_tasks)}, Skipped: {len(self.skipped_tasks)}\n"
            f"Tasks sorted by priority (high → medium → low), then shortest-first within each tier.\n"
        )
        return header + "\n".join(reasons)

    def display_plan(self) -> None:
        """Print the generated schedule and skipped tasks to the terminal."""
        print(f"\nDaily plan for {self.pet.get_info()}:")
        if not self.scheduled_tasks:
            print("  No tasks could be scheduled.")
        for task in self.scheduled_tasks:
            status = "✓" if task.completed else " "
            print(
                f"  [{status}] {task.start_time} — {task.title} "
                f"({task.duration_minutes} min) [priority: {task.priority}]"
            )
        if self.skipped_tasks:
            print("\n  Skipped:")
            for task in self.skipped_tasks:
                print(f"    - {task.title} ({task.duration_minutes} min)")
        print(f"\nReasoning:\n{self.reasoning}")
