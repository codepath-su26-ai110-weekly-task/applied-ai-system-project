import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

def make_task(**kwargs) -> Task:
    defaults = dict(title="Test task", category="walk", duration_minutes=20, priority="medium")
    defaults.update(kwargs)
    return Task(**defaults)


def make_owner(minutes: int = 90) -> Owner:
    return Owner(name="Alex", available_minutes=minutes)


def make_pet(*tasks: Task) -> Pet:
    pet = Pet(name="Biscuit", species="Dog", breed="Golden Retriever", age=3)
    for t in tasks:
        pet.add_task(t)
    return pet


def make_scheduler(tasks: list, minutes: int = 90) -> Scheduler:
    owner = make_owner(minutes)
    pet = make_pet(*tasks)
    return Scheduler(owner=owner, pet=pet, tasks=tasks)


# ---------------------------------------------------------------------------
# Original tests (kept from Phase 3)
# ---------------------------------------------------------------------------

def test_mark_complete_sets_completed_true():
    task = make_task(title="Morning walk")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = make_pet()
    assert len(pet.get_tasks()) == 0
    pet.add_task(make_task(title="Breakfast", category="feeding", duration_minutes=10, priority="high"))
    pet.add_task(make_task(title="Evening walk"))
    assert len(pet.get_tasks()) == 2


# ---------------------------------------------------------------------------
# Sorting correctness
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    t1 = make_task(title="Walk",    start_time="10:30")
    t2 = make_task(title="Feeding", start_time="08:00")
    t3 = make_task(title="Meds",    start_time="09:15")
    sched = make_scheduler([t1, t2, t3])
    sched.scheduled_tasks = [t1, t2, t3]   # bypass generate_plan for isolation

    result = sched.sort_by_time()
    assert [t.start_time for t in result] == ["08:00", "09:15", "10:30"]


def test_sort_by_time_tasks_without_start_time_go_last():
    t_timed   = make_task(title="Walk",  start_time="08:00")
    t_untimed = make_task(title="Bath",  start_time=None)
    sched = make_scheduler([t_timed, t_untimed])
    sched.scheduled_tasks = [t_untimed, t_timed]

    result = sched.sort_by_time()
    assert result[0].start_time == "08:00"
    assert result[-1].start_time is None


def test_sort_tasks_orders_high_before_low_priority():
    low  = make_task(title="Bath",    priority="low",    duration_minutes=30)
    med  = make_task(title="Play",    priority="medium", duration_minutes=20)
    high = make_task(title="Meds",    priority="high",   duration_minutes=5)
    sched = make_scheduler([low, med, high])

    result = sched.sort_tasks()
    assert result[0].priority == "high"
    assert result[-1].priority == "low"


# ---------------------------------------------------------------------------
# Recurrence logic
# ---------------------------------------------------------------------------

def test_recurring_daily_task_returns_next_occurrence():
    task = make_task(title="Morning walk", is_recurring=True, frequency="daily")
    next_task = task.mark_complete()

    assert next_task is not None
    expected_due = (date.today() + timedelta(days=1)).isoformat()
    assert next_task.due_date == expected_due
    assert next_task.completed is False
    assert next_task.start_time is None   # reset, not carried forward


def test_recurring_weekly_task_due_in_seven_days():
    task = make_task(title="Bath", is_recurring=True, frequency="weekly")
    next_task = task.mark_complete()

    expected_due = (date.today() + timedelta(weeks=1)).isoformat()
    assert next_task.due_date == expected_due


def test_non_recurring_task_returns_none_on_complete():
    task = make_task(is_recurring=False)
    result = task.mark_complete()
    assert result is None


def test_reschedule_recurring_appends_to_pet_task_list():
    task = make_task(title="Morning walk", is_recurring=True, frequency="daily")
    owner = make_owner()
    pet   = make_pet(task)
    sched = Scheduler(owner=owner, pet=pet, tasks=pet.get_tasks())

    assert len(pet.get_tasks()) == 1
    sched.reschedule_recurring(task)
    assert len(pet.get_tasks()) == 2   # original + next occurrence


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_flags_overlapping_tasks():
    t1 = make_task(title="Walk",    duration_minutes=30, start_time="09:00")
    t2 = make_task(title="Feeding", duration_minutes=10, start_time="09:15")  # starts inside Walk
    sched = make_scheduler([t1, t2])
    sched.scheduled_tasks = [t1, t2]

    warnings = sched.detect_conflicts()
    assert len(warnings) == 1
    assert "Walk" in warnings[0]
    assert "Feeding" in warnings[0]


def test_detect_conflicts_no_warning_for_sequential_tasks():
    t1 = make_task(title="Walk",    duration_minutes=30, start_time="09:00")  # ends 09:30
    t2 = make_task(title="Feeding", duration_minutes=10, start_time="09:30")  # starts exactly at end
    sched = make_scheduler([t1, t2])
    sched.scheduled_tasks = [t1, t2]

    assert sched.detect_conflicts() == []


# ---------------------------------------------------------------------------
# Schedule generation edge cases
# ---------------------------------------------------------------------------

def test_generate_plan_skips_tasks_that_exceed_budget():
    big_task   = make_task(title="Long bath",    duration_minutes=60, priority="low")
    small_task = make_task(title="Quick feeding", duration_minutes=5,  priority="high")
    sched = make_scheduler([big_task, small_task], minutes=30)
    sched.generate_plan()

    scheduled_titles = [t.title for t in sched.scheduled_tasks]
    skipped_titles   = [t.title for t in sched.skipped_tasks]
    assert "Quick feeding" in scheduled_titles
    assert "Long bath" in skipped_titles


def test_generate_plan_pet_with_no_tasks_produces_empty_schedule():
    sched = make_scheduler([], minutes=90)
    sched.generate_plan()

    assert sched.scheduled_tasks == []
    assert sched.skipped_tasks   == []


def test_generate_plan_assigns_start_times_to_all_scheduled_tasks():
    tasks = [
        make_task(title="Meds",  duration_minutes=5,  priority="high"),
        make_task(title="Walk",  duration_minutes=30, priority="medium"),
    ]
    sched = make_scheduler(tasks, minutes=60)
    sched.generate_plan()

    for task in sched.scheduled_tasks:
        assert task.start_time is not None


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def test_filter_tasks_returns_only_incomplete():
    done    = make_task(title="Done task",    completed=True)
    pending = make_task(title="Pending task", completed=False)
    sched   = make_scheduler([done, pending])

    result = sched.filter_tasks(tasks=[done, pending], completed=False)
    assert len(result) == 1
    assert result[0].title == "Pending task"


def test_filter_tasks_with_no_filter_returns_all():
    tasks = [make_task(title=f"Task {i}") for i in range(4)]
    sched = make_scheduler(tasks)
    assert len(sched.filter_tasks(tasks=tasks)) == 4
