from pawpal_system import Task, Pet, Owner, Scheduler

DIVIDER = "=" * 52

def section(title: str) -> None:
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
owner = Owner(name="Alex", available_minutes=90)

biscuit = Pet(name="Biscuit", species="Dog", breed="Golden Retriever", age=3)
mochi   = Pet(name="Mochi",   species="Cat", breed="Tabby",            age=5)
owner.add_pet(biscuit)
owner.add_pet(mochi)

# Tasks added OUT OF ORDER intentionally to test sort_by_time later
biscuit.add_task(Task(title="Fetch session",  category="enrichment", duration_minutes=20, priority="medium", is_recurring=False))
biscuit.add_task(Task(title="Flea medicine",  category="meds",       duration_minutes=5,  priority="high",   is_recurring=False))
biscuit.add_task(Task(title="Morning walk",   category="walk",       duration_minutes=30, priority="high",   is_recurring=True,  frequency="daily"))
biscuit.add_task(Task(title="Breakfast",      category="feeding",    duration_minutes=10, priority="high",   is_recurring=True,  frequency="daily"))
biscuit.add_task(Task(title="Bath time",      category="grooming",   duration_minutes=40, priority="low",    is_recurring=False))

mochi.add_task(Task(title="Breakfast",          category="feeding",    duration_minutes=5,  priority="high",   is_recurring=True,  frequency="daily"))
mochi.add_task(Task(title="Litter box clean",   category="grooming",   duration_minutes=10, priority="medium", is_recurring=True,  frequency="daily"))
mochi.add_task(Task(title="Laser pointer play", category="enrichment", duration_minutes=15, priority="low",    is_recurring=False))


# ---------------------------------------------------------------------------
# 1. Today's schedule (priority sort + time budget)
# ---------------------------------------------------------------------------
section("TODAY'S SCHEDULE")
print(f"  Owner : {owner.name}  |  Budget: {owner.available_minutes} min per pet")

schedulers: dict[str, Scheduler] = {}
for pet in owner.pets:
    sched = Scheduler(owner=owner, pet=pet, tasks=pet.get_tasks())
    sched.generate_plan()
    schedulers[pet.name] = sched

    print(f"\n  {pet.get_info()}")
    print(f"  {'-' * 48}")
    for task in sched.scheduled_tasks:
        recur = " (recurring)" if task.is_recurring else ""
        print(f"    [ ] {task.start_time}  {task.title:<22} {task.duration_minutes:>3} min  [{task.priority}]{recur}")
    if sched.skipped_tasks:
        print(f"    Skipped: {', '.join(t.title for t in sched.skipped_tasks)}")
    used = sum(t.duration_minutes for t in sched.scheduled_tasks)
    print(f"    Time used: {used} / {owner.available_minutes} min")


# ---------------------------------------------------------------------------
# 2. Sort by time (after plan is generated)
# ---------------------------------------------------------------------------
section("SORT BY START TIME  (Biscuit's scheduled tasks)")
biscuit_sched = schedulers["Biscuit"]
by_time = biscuit_sched.sort_by_time()
for task in by_time:
    print(f"  {task.start_time}  {task.title}")


# ---------------------------------------------------------------------------
# 3. Filter by completion status
# ---------------------------------------------------------------------------
section("FILTER — incomplete tasks only (all pets)")
all_scheduled = []
for sched in schedulers.values():
    all_scheduled.extend(sched.scheduled_tasks)

incomplete = schedulers["Biscuit"].filter_tasks(tasks=all_scheduled, completed=False)
print(f"  {len(incomplete)} incomplete task(s) across all pets:")
for task in incomplete:
    print(f"    - {task.title} [{task.priority}]")


# ---------------------------------------------------------------------------
# 4. Recurring task — mark complete, get next occurrence
# ---------------------------------------------------------------------------
section("RECURRING TASK — mark complete & auto-schedule next")
morning_walk = next(t for t in biscuit.get_tasks() if t.title == "Morning walk")
print(f"  Before: '{morning_walk.title}' completed={morning_walk.completed}, due_date={morning_walk.due_date}")

next_occurrence = biscuit_sched.reschedule_recurring(morning_walk)
print(f"  After:  '{morning_walk.title}' completed={morning_walk.completed}")
if next_occurrence:
    print(f"  Next occurrence added → due_date={next_occurrence.due_date}, completed={next_occurrence.completed}")
    print(f"  Biscuit now has {len(biscuit.get_tasks())} tasks (was 5)")


# ---------------------------------------------------------------------------
# 5. Conflict detection
# ---------------------------------------------------------------------------
section("CONFLICT DETECTION — two tasks at the same time")
conflict_pet = Pet(name="TestDog", species="Dog", breed="Mixed", age=2)
conflict_pet.add_task(Task(title="Walk",    category="walk",    duration_minutes=30, priority="high",   start_time="09:00"))
conflict_pet.add_task(Task(title="Feeding", category="feeding", duration_minutes=10, priority="high",   start_time="09:15"))  # overlaps Walk

conflict_sched = Scheduler(owner=owner, pet=conflict_pet, tasks=conflict_pet.get_tasks())
# Manually populate scheduled_tasks so detect_conflicts can see the pre-set start_times
conflict_sched.scheduled_tasks = conflict_pet.get_tasks()

conflicts = conflict_sched.detect_conflicts()
if conflicts:
    print("  Conflicts found:")
    for warning in conflicts:
        print(warning)
else:
    print("  No conflicts detected.")
