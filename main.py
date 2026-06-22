from pawpal_system import Task, Pet, Owner, Scheduler

# --- Setup ---
owner = Owner(name="Alex", available_minutes=90)

biscuit = Pet(name="Biscuit", species="Dog", breed="Golden Retriever", age=3)
mochi = Pet(name="Mochi", species="Cat", breed="Tabby", age=5)

owner.add_pet(biscuit)
owner.add_pet(mochi)

# --- Tasks for Biscuit ---
biscuit.add_task(Task(title="Morning walk",   category="walk",     duration_minutes=30, priority="high",   is_recurring=True))
biscuit.add_task(Task(title="Breakfast",      category="feeding",  duration_minutes=10, priority="high",   is_recurring=True))
biscuit.add_task(Task(title="Flea medicine",  category="meds",     duration_minutes=5,  priority="high",   is_recurring=False))
biscuit.add_task(Task(title="Fetch session",  category="enrichment", duration_minutes=20, priority="medium", is_recurring=False))
biscuit.add_task(Task(title="Bath time",      category="grooming", duration_minutes=40, priority="low",    is_recurring=False))

# --- Tasks for Mochi ---
mochi.add_task(Task(title="Breakfast",        category="feeding",  duration_minutes=5,  priority="high",   is_recurring=True))
mochi.add_task(Task(title="Litter box clean", category="grooming", duration_minutes=10, priority="medium", is_recurring=True))
mochi.add_task(Task(title="Laser pointer play", category="enrichment", duration_minutes=15, priority="low", is_recurring=False))

# --- Generate and display plans ---
DIVIDER = "=" * 52

print(f"\n{'TODAY\'S SCHEDULE':^52}")
print(DIVIDER)
print(f"  Owner : {owner.name}")
print(f"  Budget: {owner.get_available_time()} minutes per pet")
print(DIVIDER)

for pet in owner.pets:
    scheduler = Scheduler(owner=owner, pet=pet, tasks=pet.get_tasks())
    scheduler.generate_plan()

    print(f"\n  {pet.get_info()}")
    print(f"  {'-' * 48}")

    if scheduler.scheduled_tasks:
        for task in scheduler.scheduled_tasks:
            status = "[done]" if task.completed else "[ ]"
            recur = " (recurring)" if task.is_recurring else ""
            print(f"    {status} {task.start_time}  {task.title:<22} {task.duration_minutes:>3} min  [{task.priority}]{recur}")
    else:
        print("    No tasks could be scheduled.")

    if scheduler.skipped_tasks:
        print(f"\n    Skipped (not enough time):")
        for task in scheduler.skipped_tasks:
            print(f"      - {task.title} ({task.duration_minutes} min, {task.priority} priority)")

    used = sum(t.duration_minutes for t in scheduler.scheduled_tasks)
    print(f"\n    Time used: {used} / {owner.available_minutes} min")

print(f"\n{DIVIDER}")
print(f"{'END OF SCHEDULE':^52}\n")
