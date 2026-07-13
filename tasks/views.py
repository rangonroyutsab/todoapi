from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.throttling import UserRateThrottle
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import APIException
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
import requests
import logging

from todoapi.utils import format_success_response
from .serializers import TaskSerializer
from .models import Task

logger = logging.getLogger(__name__)


class ServiceUnavailable(APIException):
    status_code = 502
    default_detail = "AI service is temporarily unavailable."
    default_code = "service_unavailable"


class GatewayTimeout(APIException):
    status_code = 504
    default_detail = "AI service request timed out."
    default_code = "gateway_timeout"


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
    filter_backends = [DjangoFilterBackend]
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

    @action(detail=True, methods=["post"], url_path="generate-description")
    def generate_description(self, request, pk=None):
        task = self.get_object()

        # Securely retrieve API Key
        api_key = getattr(settings, "GEMINI_API_KEY", None)
        if not api_key:
            logger.error("GEMINI_API_KEY is not configured.")
            raise APIException(detail="Gemini API key is not configured.")

        title = task.title
        desc = task.description or ""

        if not desc:
            prompt = f"Generate a two-sentence description for a task with the title: '{title}'."
        else:
            prompt = f"Refine and rewrite the following task description into exactly two sentences. Task title: '{title}'. Existing description: '{desc}'."

        prompt += "\n\nCRITICAL: The response MUST be exactly two sentences long. Do not include markdown formatting, prefix, or other text. Return ONLY the description."

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code != 200:
                logger.error(f"Gemini API returned error {response.status_code}")
                raise ServiceUnavailable(
                    detail="Failed to generate description from AI service."
                )

            data = response.json()

            # Validation
            try:
                generated_text = data["candidates"][0]["content"]["parts"][0][
                    "text"
                ].strip()
                if not generated_text:
                    raise ValueError("Empty AI output")
            except (KeyError, IndexError, ValueError):
                logger.error("Failed to parse Gemini response structure.")
                raise ServiceUnavailable(
                    detail="Received invalid response format from AI service."
                )

            return format_success_response(
                data={"description": generated_text},
                message="Description generated successfully",
            )

        except requests.exceptions.Timeout:
            logger.error("Gemini API request timed out.")
            raise GatewayTimeout(detail="The request to the AI service timed out.")
        except requests.exceptions.RequestException as err:
            # Secure logging: do not print the exception representation (could contain the key)
            logging.exception(f"Gemini API connection error: {type(err).__name__}")
            raise ServiceUnavailable(detail="Could not connect to the AI service.")
