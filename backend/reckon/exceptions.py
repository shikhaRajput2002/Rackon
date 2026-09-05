from dataclasses import dataclass
from typing import Any, Dict, Optional

from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


@dataclass
class AppError:
    """Base error definition for strict API error responses."""

    error_code: str
    message: str
    status: int = 400

    def response(self, details: Optional[dict] = None, message: Optional[str] = None) -> Response:
        return Response(
            {
                "error_code": self.error_code,
                "message": message or self.message,
                "details": details or {},
            },
            status=self.status,
        )


VALIDATION_ERROR = AppError("VALIDATION_ERROR", "Invalid input data.", status=400)
MISSING_REQUIRED_PARAM = AppError("MISSING_REQUIRED_PARAM", "A required parameter is missing.", status=400)
INVALID_DATE_RANGE = AppError("INVALID_DATE_RANGE", "start_date cannot be after end_date.", status=400)


def custom_exception_handler(exc: Exception, context: Dict[str, Any]) -> Optional[Response]:
    """Wrap DRF errors into the same envelope every endpoint uses."""
    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    if isinstance(exc, exceptions.ValidationError):
        return VALIDATION_ERROR.response(details=response.data)

    if isinstance(exc, (exceptions.NotAuthenticated, exceptions.AuthenticationFailed)):
        return AppError(
            "UNAUTHORIZED",
            "Authentication credentials were not provided.",
            status=401,
        ).response()

    return response
