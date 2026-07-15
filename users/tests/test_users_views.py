import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestRegisterView:
    def test_register_user_success(self, api_client):
        url = reverse("register")
        payload = {
            "username": "newuser",
            "email": "new@test.com",
            "password": "password123",
        }
        response = api_client.post(url, payload)

        assert response.status_code == 201
        assert response.data["success"] is True
        assert "password" not in response.data["data"]
        assert response.data["data"]["username"] == "newuser"

    def test_register_duplicate_username(self, api_client, user_factory):
        # Create an existing user
        user_factory(username="existinguser")

        url = reverse("register")
        payload = {"username": "existinguser", "password": "password123"}
        response = api_client.post(url, payload)

        assert response.status_code == 400
        assert response.data["success"] is False
        assert "username" in response.data["errors"]

    def test_mocking_creation_failure(self, api_client, mocker):
        # Mocking the create method to simulate a failure and check the exception handler
        mocker.patch(
            "users.views.RegisterView.perform_create", side_effect=Exception("DB Error")
        )
        url = reverse("register")
        payload = {
            "username": "failuser",
            "password": "password123",
            "email": "f@f.com",
        }

        # Depending on DRF exception handling setup, an unhandled exception
        # may throw a 500. DRF only catches APIException by default, standard Exceptions result in 500.
        with pytest.raises(Exception, match="DB Error"):
            api_client.post(url, payload)


@pytest.mark.django_db
class TestLoginView:
    def test_login_success(self, api_client, user_factory):
        # The factory uses "securepassword123" by default
        user_factory(username="testuser")

        url = reverse("login")
        payload = {"username": "testuser", "password": "securepassword123"}
        response = api_client.post(url, payload)

        assert response.status_code == 200
        assert response.data["success"] is True
        assert "access" in response.data["data"]
        assert "refresh" in response.data["data"]

    def test_login_invalid_credentials(self, api_client, user_factory):
        user_factory(username="testuser")

        url = reverse("login")
        payload = {"username": "testuser", "password": "wrongpassword"}
        response = api_client.post(url, payload)

        assert response.status_code == 401
        assert "detail" in response.data["errors"]

    def test_login_missing_credentials(self, api_client):
        url = reverse("login")
        payload = {"username": "testuser"}
        response = api_client.post(url, payload)

        assert response.status_code == 400
        assert "password" in response.data["errors"]
