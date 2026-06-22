import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet


def make_task(**kwargs):
    defaults = dict(title="Test task", category="walk", duration_minutes=20, priority="medium")
    defaults.update(kwargs)
    return Task(**defaults)


def test_mark_complete_sets_completed_true():
    task = make_task(title="Morning walk")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Biscuit", species="Dog", breed="Golden Retriever", age=3)
    assert len(pet.get_tasks()) == 0
    pet.add_task(make_task(title="Breakfast", category="feeding", duration_minutes=10, priority="high"))
    pet.add_task(make_task(title="Evening walk"))
    assert len(pet.get_tasks()) == 2
