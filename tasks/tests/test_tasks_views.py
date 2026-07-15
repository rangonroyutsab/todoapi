import pytest
from django.urls import reverse
from unittest.mock import patch
from rest_framework import status


@pytest.mark.django_db
class TestTaskViewSet:
    def test_list_tasks_authenticated(self, auth_client, task_factory):
        task_factory(owner=auth_client.user)
        task_factory()  # Owned by someone else

        url = reverse("task-list")
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert len(response.data["data"]) == 1  # Only owner's tasks

    def test_create_task(self, auth_client):
        url = reverse("task-list")
        data = {"title": "New Task"}
        response = auth_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["data"]["title"] == "New Task"
        assert response.data["data"]["status"] == "pending"

    def test_unauthenticated_access(self, api_client):
        url = reverse("task-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_filter_by_status(self, auth_client, task_factory):
        task_factory(owner=auth_client.user, status="pending")
        task_factory(owner=auth_client.user, status="done")

        url = reverse("task-list") + "?status=done"
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 1
        assert response.data["data"][0]["status"] == "done"

    def test_update_task(self, auth_client, task_factory):
        task = task_factory(owner=auth_client.user, title="Old Title")
        url = reverse("task-detail", kwargs={"pk": task.id})
        data = {"title": "Updated Title", "status": "done"}
        
        response = auth_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["title"] == "Updated Title"
        assert response.data["data"]["status"] == "done"

    def test_delete_task(self, auth_client, task_factory):
        task = task_factory(owner=auth_client.user)
        url = reverse("task-detail", kwargs={"pk": task.id})
        
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_200_OK

    def test_list_tasks_unpaginated(self, auth_client, task_factory):
        task_factory(owner=auth_client.user)
        url = reverse("task-list")
        with patch("tasks.views.TaskViewSet.pagination_class", None):
            response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "meta" not in response.data

    def test_retrieve_task(self, auth_client, task_factory):
        task = task_factory(owner=auth_client.user)
        url = reverse("task-detail", kwargs={"pk": task.id})
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["title"] == task.title


@pytest.mark.django_db
class TestGenerateDescriptionAction:
    def test_generate_description_success(self, auth_client, task_factory, mocker):
        task = task_factory(owner=auth_client.user, title="Write tests")

        # Mock requests.post to avoid real network call
        mock_post = mocker.patch("tasks.views.requests.post")
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "Write the pytest tests. Ensure all edge cases are covered."
                            }
                        ]
                    }
                }
            ]
        }

        url = reverse("task-generate-description", kwargs={"pk": task.id})
        response = auth_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["description"] == "Write the pytest tests. Ensure all edge cases are covered."
        mock_post.assert_called_once()

    def test_generate_description_service_unavailable(self, auth_client, task_factory, mocker):
        task = task_factory(owner=auth_client.user)
        
        mock_post = mocker.patch("tasks.views.requests.post")
        mock_post.return_value.status_code = 500

        url = reverse("task-generate-description", kwargs={"pk": task.id})
        response = auth_client.post(url)

        assert response.status_code == status.HTTP_502_BAD_GATEWAY
        assert response.data["success"] is False

    @patch("tasks.views.settings")
    def test_generate_description_missing_api_key(self, mock_settings, auth_client, task_factory):
        mock_settings.GEMINI_API_KEY = None
        task = task_factory(owner=auth_client.user)
        url = reverse("task-generate-description", kwargs={"pk": task.id})
        response = auth_client.post(url)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Gemini API key is not configured" in str(response.data)

    def test_generate_description_empty_description(self, auth_client, task_factory, mocker):
        task = task_factory(owner=auth_client.user, description="")
        mock_post = mocker.patch("tasks.views.requests.post")
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "Fresh AI Description"}]}}]
        }
        url = reverse("task-generate-description", kwargs={"pk": task.id})
        response = auth_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        mock_post.assert_called_once()
        assert "Fresh AI Description" in response.data["data"]["description"]

    def test_generate_description_malformed_response(self, auth_client, task_factory, mocker):
        task = task_factory(owner=auth_client.user)
        mock_post = mocker.patch("tasks.views.requests.post")
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"bad": "data"}
        url = reverse("task-generate-description", kwargs={"pk": task.id})
        response = auth_client.post(url)
        assert response.status_code == status.HTTP_502_BAD_GATEWAY
        assert response.data["success"] is False

    def test_generate_description_timeout(self, auth_client, task_factory, mocker):
        import requests
        task = task_factory(owner=auth_client.user)
        mock_post = mocker.patch("tasks.views.requests.post")
        mock_post.side_effect = requests.exceptions.Timeout("Timed out")
        url = reverse("task-generate-description", kwargs={"pk": task.id})
        response = auth_client.post(url)
        assert response.status_code == status.HTTP_504_GATEWAY_TIMEOUT
        assert response.data["success"] is False

    def test_generate_description_connection_error(self, auth_client, task_factory, mocker):
        import requests
        task = task_factory(owner=auth_client.user)
        mock_post = mocker.patch("tasks.views.requests.post")
        mock_post.side_effect = requests.exceptions.RequestException("Connection Failed")
        url = reverse("task-generate-description", kwargs={"pk": task.id})
        response = auth_client.post(url)
        assert response.status_code == status.HTTP_502_BAD_GATEWAY
        assert response.data["success"] is False

    def test_generate_description_empty_ai_output(self, auth_client, task_factory, mocker):
        task = task_factory(owner=auth_client.user)
        mock_post = mocker.patch("tasks.views.requests.post")
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "   "}]}}]
        }
        url = reverse("task-generate-description", kwargs={"pk": task.id})
        response = auth_client.post(url)
        assert response.status_code == status.HTTP_502_BAD_GATEWAY
        assert response.data["success"] is False
