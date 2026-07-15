import pytest
from tasks.models import Task


@pytest.mark.django_db
def test_task_string_representation(task_factory):
    task = task_factory(title="My Task", status="pending")
    assert str(task) == f"Task(id={task.id}: My Task, pending)"


@pytest.mark.django_db
def test_task_default_status(user_factory):
    user = user_factory()
    task = Task.objects.create(title="New Task", owner=user)
    assert task.status == "pending"
    assert task.description == ""
