import pytest
from rest_framework.test import APIClient

from testing.factories import UserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_factory():
    return UserFactory
