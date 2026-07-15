from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
import logging

from todoapi.utils import format_success_response
from .serializers import TaskSerializer
from .models import Task
from .filters import TaskOrderingFilter
from .services import get_description_service

logger = logging.getLogger(__name__)


class GenerateDescriptionMinThrottle(UserRateThrottle):
    scope = "generate_description_min"


class GenerateDescriptionDayThrottle(UserRateThrottle):
    scope = "generate_description_day"


class TaskPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 100


class TaskViewSet(viewsets.ModelViewSet):
    """API endpoints for managing To-Do tasks."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = TaskPagination
    filter_backends = [DjangoFilterBackend, TaskOrderingFilter]
    filterset_fields = ["status"]

    def get_throttles(self):
        if self.action == "generate_description":
            return [GenerateDescriptionMinThrottle(), GenerateDescriptionDayThrottle()]
        return super().get_throttles()

    def get_queryset(self):
        """Restrict tasks to only those owned by the authenticated user."""
        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """Automatically associate the task with the authenticated user."""
        serializer.save(owner=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        meta = None
        if page is not None:
            queryset = page
            paginator = self.paginator
            meta = {
                "page": paginator.page.number,
                "limit": paginator.get_page_size(request),
                "total": paginator.page.paginator.count,
                "totalPages": paginator.page.paginator.num_pages,
            }

        serializer = self.get_serializer(queryset, many=True)
        return format_success_response(
            data=serializer.data, message="Tasks retrieved successfully", meta=meta
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
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="generate-description")
    def generate_description(self, request, pk=None):
        task = self.get_object()

        service = get_description_service()
        generated_text = service.generate(task.title, task.description)

        return format_success_response(
            data={"description": generated_text},
            message="Description generated successfully",
        )
