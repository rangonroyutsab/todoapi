import pytest
from rest_framework.test import APIClient
import factory
from django.contrib.auth import get_user_model
from tasks.models import Task

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = "password123"


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    title = factory.Sequence(lambda n: f"Task {n}")
    description = "Test description"
    owner = factory.SubFactory(UserFactory)
    status = "pending"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client):
    user = UserFactory()
    api_client.force_authenticate(user=user)
    api_client.user = user
    return api_client

@pytest.fixture
def user_factory():
    return UserFactory

@pytest.fixture
def task_factory():
    return TaskFactory

