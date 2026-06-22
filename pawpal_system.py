from dataclasses import dataclass, field
from typing import Optional

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
DEFAULT_START_HOUR = 8  # plans begin at 08:00


@dataclass
class Task:
    title: str
    category: str              # walk | feeding | meds | grooming | enrichment
    duration_minutes: int
    priority: str              # high | medium | low
    is_recurring: bool = False
    frequency: str = "daily"   # daily | weekly
    start_time: Optional[str] = None  # set by Scheduler when building a plan
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

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
        }


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


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, tasks: list):
        self.owner = owner
        self.pet = pet
        self.tasks = tasks
        self.available_minutes = owner.available_minutes
        self.scheduled_tasks: list[Task] = []
        self.skipped_tasks: list[Task] = []
        self.reasoning: str = ""

    def sort_tasks(self, tasks: Optional[list] = None) -> list:
        """Sort tasks by priority (high first), then by duration ascending within each tier."""
        source = tasks if tasks is not None else self.tasks
        return sorted(source, key=lambda t: (PRIORITY_ORDER.get(t.priority, 99), t.duration_minutes))

    def filter_by_time(self, tasks: list, remaining_minutes: int) -> list:
        """Return only the tasks whose duration fits within the remaining time budget."""
        return [t for t in tasks if t.duration_minutes <= remaining_minutes]

    def generate_plan(self) -> None:
        """Build the daily schedule, populating scheduled_tasks, skipped_tasks, and reasoning."""
        self.scheduled_tasks = []
        self.skipped_tasks = []
        reasons: list[str] = []

        sorted_tasks = self.sort_tasks()
        remaining = self.available_minutes
        current_hour = DEFAULT_START_HOUR
        current_minute = 0

        for task in sorted_tasks:
            if task.duration_minutes <= remaining:
                task.start_time = f"{current_hour:02d}:{current_minute:02d}"
                self.scheduled_tasks.append(task)
                remaining -= task.duration_minutes
                reasons.append(
                    f"  - {task.title} ({task.priority} priority) → {task.start_time}"
                )
                total_minutes = current_hour * 60 + current_minute + task.duration_minutes
                current_hour = total_minutes // 60
                current_minute = total_minutes % 60
            else:
                self.skipped_tasks.append(task)
                reasons.append(
                    f"  - {task.title} skipped (needs {task.duration_minutes} min, only {remaining} min left)"
                )

        self.reasoning = self._build_reasoning(reasons)

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
