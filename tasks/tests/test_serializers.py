import pytest
from tasks.serializers import TaskSerializer


@pytest.mark.django_db
def test_task_serializer_valid_data(user_factory):
    user = user_factory()
    data = {"title": "Test Task", "description": "Desc"}
    serializer = TaskSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.validated_data["title"] == "Test Task"


@pytest.mark.django_db
def test_task_serializer_read_only_fields():
    data = {"title": "Task", "id": 999, "created_at": "2024-01-01"}
    serializer = TaskSerializer(data=data)
    assert serializer.is_valid()
    assert "id" not in serializer.validated_data
    assert "created_at" not in serializer.validated_data
