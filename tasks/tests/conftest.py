import pytest
from testing.factories import UserFactory, TaskFactory


@pytest.fixture
def auth_client(api_client):
    user = UserFactory()
    api_client.force_authenticate(user=user)
    api_client.user = user
    return api_client


@pytest.fixture
def task_factory():
    return TaskFactory
