import logging
from functools import wraps
from typing import Callable, TypeAlias

from django.db import transaction
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
    StreamingHttpResponse,
)
from django.utils import timezone

from request_logger.models import RequestLog

logger = logging.getLogger(__name__)

# if the reference arg is not a fixed str, it must be a callable
ReferenceFunc: TypeAlias = Callable[[HttpRequest], str]


def log_request_response(
    *,
    request: HttpRequest,
    response: HttpResponse,
    reference: str,
    duration: float,
) -> RequestLog:
    """Create RequestLog from request and response objects."""
    location = getattr(response, "url", "")
    if isinstance(response, HttpResponseRedirect):
        location = response.url
    else:
        location = ""
    if not isinstance(response, StreamingHttpResponse):
        content_length = len(response.content)
    else:
        content_length = None
    content_type = response.headers.get("Content-Type", "")
    return RequestLog.objects.create(
        request=request,
        reference=reference,
        duration=duration,
        response_status_code=response.status_code,
        response_location=location,
        response_content_length=content_length,
        response_content_type=content_type,
    )


@transaction.atomic
def log_request(reference: str | ReferenceFunc) -> Callable:
    """Decorate view function to log a request-response."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def inner_func(
            request: HttpRequest, *args: object, **kwargs: object
        ) -> HttpResponse:
            if isinstance(reference, str):
                request_reference = reference
            elif callable(reference):
                request_reference = reference(request)
            else:
                raise ValueError("Invalid reference argument - must be str or func.")
            start_ts = timezone.now()
            response = func(request, *args, **kwargs)
            duration = (timezone.now() - start_ts).total_seconds()
            try:
                log_request_response(
                    request=request,
                    response=response,
                    reference=request_reference,
                    duration=duration,
                )
            except Exception:  # noqa: B902
                logger.exception("Error storing RequestLog.")
            return response

        return inner_func

    return decorator
