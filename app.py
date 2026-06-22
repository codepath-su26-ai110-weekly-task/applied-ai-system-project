import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state — persists objects across Streamlit reruns
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None          # Owner instance created on setup

# ---------------------------------------------------------------------------
# Section 1 — Owner setup
# ---------------------------------------------------------------------------
st.subheader("1. Owner Setup")

with st.form("owner_form"):
    owner_name = st.text_input("Your name", value="Alex")
    available_minutes = st.number_input(
        "Minutes available for pet care today", min_value=10, max_value=480, value=90, step=5
    )
    submitted = st.form_submit_button("Save owner")

if submitted:
    # Preserve existing pets if the owner was already set up
    existing_pets = st.session_state.owner.pets if st.session_state.owner else []
    st.session_state.owner = Owner(name=owner_name, available_minutes=int(available_minutes))
    for pet in existing_pets:
        st.session_state.owner.add_pet(pet)
    st.success(f"Owner saved: {owner_name} ({available_minutes} min/day)")

owner: Owner | None = st.session_state.owner

if owner:
    st.caption(f"Current owner: **{owner.name}** — {owner.available_minutes} min available")

st.divider()

# ---------------------------------------------------------------------------
# Section 2 — Add a pet  (only after owner is set up)
# ---------------------------------------------------------------------------
st.subheader("2. Add a Pet")

if not owner:
    st.info("Save your owner info above before adding pets.")
else:
    with st.form("pet_form"):
        col1, col2 = st.columns(2)
        with col1:
            pet_name  = st.text_input("Pet name", value="Biscuit")
            species   = st.selectbox("Species", ["Dog", "Cat", "Rabbit", "Other"])
        with col2:
            breed     = st.text_input("Breed", value="Golden Retriever")
            age       = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
        add_pet = st.form_submit_button("Add pet")

    if add_pet:
        # Prevent duplicate pet names
        existing_names = [p.name for p in owner.pets]
        if pet_name in existing_names:
            st.warning(f"{pet_name} is already in your list.")
        else:
            owner.add_pet(Pet(name=pet_name, species=species, breed=breed, age=int(age)))
            st.success(f"Added {pet_name} the {breed}!")

    if owner.pets:
        st.write("**Your pets:**")
        for pet in owner.pets:
            st.markdown(f"- {pet.get_info()}")

st.divider()

# ---------------------------------------------------------------------------
# Section 3 — Add tasks to a pet  (only after at least one pet exists)
# ---------------------------------------------------------------------------
st.subheader("3. Add Tasks")

if not owner or not owner.pets:
    st.info("Add at least one pet before adding tasks.")
else:
    pet_names = [p.name for p in owner.pets]

    selected_pet_name = st.selectbox("Select pet to add tasks to", pet_names)
    selected_pet: Pet = next(p for p in owner.pets if p.name == selected_pet_name)

    with st.form("task_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
            category   = st.selectbox("Category", ["walk", "feeding", "meds", "grooming", "enrichment"])
        with col2:
            duration   = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
            priority   = st.selectbox("Priority", ["high", "medium", "low"])
        with col3:
            is_recurring = st.checkbox("Recurring?", value=True)
            frequency    = st.selectbox("Frequency", ["daily", "weekly"])
        add_task = st.form_submit_button("Add task")

    if add_task:
        selected_pet.add_task(Task(
            title=task_title,
            category=category,
            duration_minutes=int(duration),
            priority=priority,
            is_recurring=is_recurring,
            frequency=frequency,
        ))
        st.success(f"Added '{task_title}' to {selected_pet.name}'s tasks.")

    if selected_pet.get_tasks():
        st.write(f"**{selected_pet.name}'s current tasks:**")
        st.table([t.to_dict() for t in selected_pet.get_tasks()])
    else:
        st.info(f"No tasks yet for {selected_pet.name}.")

st.divider()

# ---------------------------------------------------------------------------
# Section 4 — Generate schedule
# ---------------------------------------------------------------------------
st.subheader("4. Generate Today's Schedule")

if not owner or not owner.pets:
    st.info("Add an owner and at least one pet before generating a schedule.")
elif not owner.get_all_tasks():
    st.info("Add at least one task before generating a schedule.")
else:
    if st.button("Generate schedule"):
        st.markdown("---")
        for pet in owner.pets:
            if not pet.get_tasks():
                continue

            scheduler = Scheduler(owner=owner, pet=pet, tasks=pet.get_tasks())
            scheduler.generate_plan()

            st.markdown(f"### {pet.get_info()}")

            if scheduler.scheduled_tasks:
                rows = []
                for task in scheduler.scheduled_tasks:
                    rows.append({
                        "Time": task.start_time,
                        "Task": task.title,
                        "Category": task.category,
                        "Duration (min)": task.duration_minutes,
                        "Priority": task.priority,
                        "Recurring": "Yes" if task.is_recurring else "No",
                    })
                st.table(rows)
            else:
                st.warning("No tasks could be scheduled within the time budget.")

            if scheduler.skipped_tasks:
                skipped_names = ", ".join(t.title for t in scheduler.skipped_tasks)
                st.caption(f"Skipped (not enough time): {skipped_names}")

            used = sum(t.duration_minutes for t in scheduler.scheduled_tasks)
            st.progress(used / owner.available_minutes, text=f"Time used: {used} / {owner.available_minutes} min")

            with st.expander("Scheduling reasoning"):
                st.text(scheduler.reasoning)

            st.markdown("---")
