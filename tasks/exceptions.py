from rest_framework.exceptions import APIException


class ServiceUnavailable(APIException):
    """Returned when an external service is unavailable or returns errors."""

    status_code = 502
    default_detail = "AI service is temporarily unavailable."
    default_code = "service_unavailable"


class GatewayTimeout(APIException):
    """Returned when an external service request times out."""

    status_code = 504
    default_detail = "AI service request timed out."
    default_code = "gateway_timeout"
