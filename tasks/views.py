from rest_framework import viewsets, status
from django.http import Http404
from .serializers import TaskSerializer
from .models import Task
from todoapi.utils import format_success_response


class TaskViewSet(viewsets.ViewSet):
    """API endpoints for managing To-Do tasks."""

    def list(self, request):
        """Retrieves a paginated, sorted, and optionally filtered list of tasks."""
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

        sort_by = request.query_params.get("sort_by", "created_at")
        if sort_by not in ("created_at", "updated_at"):
            sort_by = "created_at"

        db_sort_by = sort_by

        order = request.query_params.get("order", "desc")
        if order not in ("asc", "desc"):
            order = "desc"

        order_prefix = "-" if order == "desc" else ""

        queryset = Task.objects.all()
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        queryset = queryset.order_by(f"{order_prefix}{db_sort_by}")

        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        tasks = queryset[start:end]

        serializer = TaskSerializer(tasks, many=True)

        total_pages = (total + limit - 1) // limit if limit > 0 else 0
        meta = {"page": page, "limit": limit, "total": total, "totalPages": total_pages}

        return format_success_response(
            data=serializer.data, message="Tasks retrieved successfully", meta=meta
        )

    def create(self, request):
        """Creates a new task."""
        serializer = TaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return format_success_response(
            data=serializer.data,
            message="Task created successfully",
            status_code=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, pk=None):
        """Retrieves a single task by its ID."""
        try:
            task = Task.objects.get(pk=pk)
        except (Task.DoesNotExist, ValueError):
            raise Http404("Task not found")

        serializer = TaskSerializer(task)
        return format_success_response(
            data=serializer.data, message="Task retrieved successfully"
        )

    def update(self, request, pk=None):
        """Updates a specific task by its ID."""
        try:
            task = Task.objects.get(pk=pk)
        except (Task.DoesNotExist, ValueError):
            raise Http404("Task not found")

        serializer = TaskSerializer(task, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return format_success_response(
            data=serializer.data, message="Task updated successfully"
        )

    def destroy(self, request, pk=None):
        """Deletes a task by its ID."""
        try:
            task = Task.objects.get(pk=pk)
        except (Task.DoesNotExist, ValueError):
            raise Http404("Task not found")

        task.delete()

        return format_success_response(
            data=None,
            message="Task deleted successfully",
            status_code=status.HTTP_200_OK,
        )
