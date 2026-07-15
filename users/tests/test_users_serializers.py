import pytest
from users.serializers import UserRegistrationSerializer


@pytest.mark.django_db
def test_valid_user_registration_serializer():
    data = {
        "username": "testuser",
        "email": "test@test.com",
        "password": "validpassword",
    }
    serializer = UserRegistrationSerializer(data=data)
    assert serializer.is_valid()
    user = serializer.save()
    assert user.username == "testuser"
    assert user.email == "test@test.com"
    assert user.check_password("validpassword")


@pytest.mark.django_db
def test_serializer_short_password():
    data = {"username": "testuser", "email": "test@test.com", "password": "short"}
    serializer = UserRegistrationSerializer(data=data)
    assert not serializer.is_valid()
    assert "password" in serializer.errors


@pytest.mark.django_db
def test_serializer_missing_required_fields():
    data = {"email": "test@test.com"}
    serializer = UserRegistrationSerializer(data=data)
    assert not serializer.is_valid()
    assert "username" in serializer.errors
    assert "password" in serializer.errors


@pytest.mark.django_db
def test_serializer_duplicate_username(user_factory):
    # Setup: create existing user
    user_factory(username="existinguser")

    # Try creating another with the same username
    data = {
        "username": "existinguser",
        "email": "new@test.com",
        "password": "validpassword",
    }
    serializer = UserRegistrationSerializer(data=data)

    assert not serializer.is_valid()
    assert "username" in serializer.errors
