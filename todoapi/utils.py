from rest_framework.views import exception_handler
from rest_framework.response import Response


def format_success_response(data, message="Success", meta=None, status_code=200):
    """Formats a successful API response according to the defined specification.

    Args:
        data: The main payload to return in the response body.
        message: An optional success message (defaults to "Success").
        meta: Optional pagination metadata dictionary containing page, limit, total, and totalPages.
        status_code: The HTTP status code to return (defaults to 200 OK).

    Returns:
        A DRF Response object structured with success, message, data, and optionally meta fields.
    """
    response_data = {
        "success": True,
        "message": message,
        "data": data,
    }
    if meta is not None:
        response_data["meta"] = meta
    return Response(response_data, status=status_code)


def custom_exception_handler(exc, context):
    """Intercepts and formats exceptions into the specified error response structure.

    Args:
        exc: The exception instance raised.
        context: The context in which the exception occurred.

    Returns:
        A formatted DRF Response object if the exception is handled, otherwise None.
        The response includes success, message, and errors fields.
    """
    response = exception_handler(exc, context)

    if response is not None:
        message = "An error occurred"
        if response.status_code == 400:
            message = "Validation Error"
        elif response.status_code == 404:
            message = "Not Found"

        custom_response_data = {
            "success": False,
            "message": message,
            "errors": response.data,
        }
        response.data = custom_response_data

    return response
