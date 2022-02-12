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

# if the reference arg is not a fixed str, it must be a callable
ReferenceFunc: TypeAlias = Callable[[HttpRequest], str]


@transaction.atomic
def log_request(reference: str | ReferenceFunc) -> Callable:
    """Decorate view function to log a request-response."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def inner_func(
            request: HttpRequest, *args: object, **kwargs: object
        ) -> HttpResponse:
            start_ts = timezone.now()
            response = func(request, *args, **kwargs)
            duration = (timezone.now() - start_ts).total_seconds()
            location = getattr(response, "url", "")
            if isinstance(reference, str):
                request_reference = reference
            elif callable(reference):
                request_reference = reference(request)
            else:
                raise ValueError("Invalid reference argument - must be str or func.")
            if isinstance(response, HttpResponseRedirect):
                location = response.url
            else:
                location = ""
            if not isinstance(response, StreamingHttpResponse):
                content_length = len(response.content)
            else:
                content_length = None
            _ = RequestLog.objects.create(
                request=request,
                reference=request_reference,
                duration=duration,
                response_status_code=response.status_code,
                response_location=location,
                response_content_length=content_length,
            )
            return response

        return inner_func

    return decorator
