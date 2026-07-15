from rest_framework.filters import BaseFilterBackend
from rest_framework.exceptions import ValidationError

ALLOWED_SORT_FIELDS = {"created_at", "updated_at"}
DEFAULT_SORT_FIELD = "created_at"
DEFAULT_SORT_ORDER = "desc"


class TaskOrderingFilter(BaseFilterBackend):
    """Custom ordering filter using sort_by and order query parameters.

    Preserves the existing API contract:
        ?sort_by=created_at&order=desc  (default)
        ?sort_by=updated_at&order=asc

    Raises ValidationError for unrecognized sort fields (fail-fast).
    """

    def filter_queryset(self, request, queryset, view):
        sort_by = request.query_params.get("sort_by")
        order = request.query_params.get("order", DEFAULT_SORT_ORDER)

        if sort_by is None:
            sort_by = DEFAULT_SORT_FIELD
        elif sort_by not in ALLOWED_SORT_FIELDS:
            raise ValidationError(
                {
                    "sort_by": (
                        f"Invalid sort field '{sort_by}'. "
                        f"Allowed: {', '.join(sorted(ALLOWED_SORT_FIELDS))}"
                    )
                }
            )

        prefix = "-" if order.lower() == "desc" else ""
        return queryset.order_by(f"{prefix}{sort_by}")
