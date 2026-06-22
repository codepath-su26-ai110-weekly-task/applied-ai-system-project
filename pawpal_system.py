from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int

    def get_info(self) -> str:
        pass

    def summary(self) -> str:
        pass


@dataclass
class Task:
    title: str
    category: str          # walk | feeding | meds | grooming | enrichment
    duration_minutes: int
    priority: str          # high | medium | low
    is_recurring: bool = False
    frequency: str = "daily"  # daily | weekly

    def is_high_priority(self) -> bool:
        pass

    def to_dict(self) -> dict:
        pass


class Owner:
    def __init__(self, name: str, available_minutes: int, preferences: Optional[dict] = None):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences: dict = preferences or {}

    def get_available_time(self) -> int:
        pass

    def update_preferences(self, prefs: dict) -> None:
        pass


class DailyPlan:
    def __init__(self, date: str):
        self.date = date
        self.scheduled_tasks: list[Task] = []
        self.skipped_tasks: list[Task] = []
        self.reasoning: str = ""

    def display(self) -> None:
        pass

    def total_duration(self) -> int:
        pass

    def get_summary(self) -> str:
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, tasks: list[Task]):
        self.owner = owner
        self.pet = pet
        self.tasks = tasks
        self.available_minutes = owner.available_minutes

    def generate_plan(self, date: str) -> DailyPlan:
        pass

    def sort_tasks(self) -> list[Task]:
        pass

    def filter_by_time(self, tasks: list[Task], remaining_minutes: int) -> list[Task]:
        pass

    def explain_reasoning(self, plan: DailyPlan) -> str:
        pass
