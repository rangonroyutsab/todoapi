from rest_framework import viewsets, status
from django.http import Http404
from .store import store
from .serializers import TaskSerializer, TaskUpdateSerializer
from todoapi.utils import format_success_response


class TaskViewSet(viewsets.ViewSet):
    """API endpoints for managing To-Do tasks without a database backend.

    Implements custom handlers for listing, creating, retrieving,
    updating, and deleting tasks utilizing the InMemoryTaskStore.
    """

    def list(self, request):
        """Retrieves a paginated, sorted, and optionally filtered list of tasks.

        Args:
            request: The incoming HTTP GET request containing query parameters.

        Returns:
            A formatted JSON response containing the list of tasks and pagination metadata.
        """
        status_filter = request.query_params.get("status")
        try:
            page = int(request.query_params.get("page", 1))
            if page < 1:
                page = 1
        except ValueError:
            page = 1

        try:
            limit = int(request.query_params.get("limit", 10))
            if limit < 1:
                limit = 1
            elif limit > 100:
                limit = 100
        except ValueError:
            limit = 10

        sort_by = request.query_params.get("sort_by", "createdAt")
        if sort_by not in ("createdAt", "updatedAt"):
            sort_by = "createdAt"

        order = request.query_params.get("order", "desc")
        if order not in ("asc", "desc"):
            order = "desc"

        tasks, total = store.get_all(
            status=status_filter, sort_by=sort_by, order=order, page=page, limit=limit
        )

        serializer = TaskSerializer(tasks, many=True)

        total_pages = (total + limit - 1) // limit if limit > 0 else 0
        meta = {"page": page, "limit": limit, "total": total, "totalPages": total_pages}

        return format_success_response(
            data=serializer.data, message="Tasks retrieved successfully", meta=meta
        )

    def create(self, request):
        """Creates a new task.

        Args:
            request: The incoming HTTP POST request containing task data.

        Returns:
            A formatted JSON response containing the created task data.
        """
        serializer = TaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        description = serializer.validated_data.get("description")
        if description is None:
            description = ""

        task = store.create(
            title=serializer.validated_data["title"],
            description=description,
        )

        response_serializer = TaskSerializer(task)
        return format_success_response(
            data=response_serializer.data,
            message="Task created successfully",
            status_code=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, pk=None):
        """Retrieves a single task by its ID.

        Args:
            request: The incoming HTTP GET request.
            pk: The primary key (ID) of the task to retrieve.

        Returns:
            A formatted JSON response containing the task data.

        Raises:
            Http404: If the task ID is invalid or not found.
        """
        try:
            task_id = int(pk)
        except ValueError:
            raise Http404("Task not found")

        task = store.get_by_id(task_id)
        if not task:
            raise Http404("Task not found")

        serializer = TaskSerializer(task)
        return format_success_response(
            data=serializer.data, message="Task retrieved successfully"
        )

    def update(self, request, pk=None):
        """Partially updates a specific task by its ID.

        Args:
            request: The incoming HTTP PUT request containing fields to update.
            pk: The primary key (ID) of the task to update.

        Returns:
            A formatted JSON response containing the updated task data.

        Raises:
            Http404: If the task ID is invalid or not found.
        """
        try:
            task_id = int(pk)
        except ValueError:
            raise Http404("Task not found")

        task = store.get_by_id(task_id)
        if not task:
            raise Http404("Task not found")

        serializer = TaskUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_task = store.update(task_id, serializer.validated_data)

        response_serializer = TaskSerializer(updated_task)
        return format_success_response(
            data=response_serializer.data, message="Task updated successfully"
        )

    def destroy(self, request, pk=None):
        """Deletes a task by its ID.

        Args:
            request: The incoming HTTP DELETE request.
            pk: The primary key (ID) of the task to delete.

        Returns:
            A formatted JSON response confirming the deletion without a data body.

        Raises:
            Http404: If the task ID is invalid or not found.
        """
        try:
            task_id = int(pk)
        except ValueError:
            raise Http404("Task not found")

        if not store.delete(task_id):
            raise Http404("Task not found")

        return format_success_response(
            data=None,
            message="Task deleted successfully",
            status_code=status.HTTP_200_OK,
        )
