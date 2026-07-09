from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from todoapi.utils import format_success_response
from .serializers import TaskSerializer
from .models import Task


class TaskPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 100


class TaskViewSet(viewsets.ModelViewSet):
    """API endpoints for managing To-Do tasks."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = TaskPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]

    def get_queryset(self):
        """Restrict tasks to only those owned by the authenticated user."""
        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """Automatically associate the task with the authenticated user."""
        serializer.save(owner=self.request.user)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        sort_by = self.request.query_params.get("sort_by", "created_at")
        order = self.request.query_params.get("order", "desc")

        if sort_by in ["created_at", "updated_at"]:
            prefix = "-" if order.lower() == "desc" else ""
            queryset = queryset.order_by(f"{prefix}{sort_by}")

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginator = self.paginator
            meta = {
                "page": paginator.page.number,
                "limit": paginator.get_page_size(request),
                "total": paginator.page.paginator.count,
                "totalPages": paginator.page.paginator.num_pages,
            }
            return format_success_response(
                data=serializer.data, message="Tasks retrieved successfully", meta=meta
            )

        serializer = self.get_serializer(queryset, many=True)
        return format_success_response(
            data=serializer.data, message="Tasks retrieved successfully"
        )

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return format_success_response(
            data=response.data,
            message="Task created successfully",
            status_code=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return format_success_response(
            data=response.data, message="Task retrieved successfully"
        )

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return format_success_response(
            data=response.data, message="Task updated successfully"
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return format_success_response(
            data=None,
            message="Task deleted successfully",
            status_code=status.HTTP_200_OK,
        )
