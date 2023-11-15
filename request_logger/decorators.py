from __future__ import annotations

import logging
from functools import wraps
from types import TracebackType
from typing import Callable, TypeAlias

from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.utils import timezone

from request_logger.models import RequestLog
from request_logger.settings import DEFAULT_EXCLUDE_FUNC, DEFAULT_INCLUDE_FUNC

logger = logging.getLogger(__name__)

# if the reference arg is not a fixed str, it must be a callable
ReferenceFunc: TypeAlias = Callable[[HttpRequest], str]
# functions used to filter in/out request to log
RequestFilterFunc: TypeAlias = Callable[[HttpRequest], bool]


class Timer:
    """Context manager used to time a function call."""

    def __enter__(self) -> Timer:
        self.start_ts = timezone.now()
        return self

    def __exit__(
        self,
        exc_type: type | None,
        exc_value: Exception | None,
        traceback: TracebackType | None,
    ) -> None:
        self.end_ts = timezone.now()

    @property
    def duration(self) -> float:
        return (self.end_ts - self.start_ts).total_seconds()


@transaction.atomic
def log_request(
    include: RequestFilterFunc = DEFAULT_INCLUDE_FUNC,
    exclude: RequestFilterFunc = DEFAULT_EXCLUDE_FUNC,
) -> Callable:
    """
    Decorate view function to log a request-response.

    The two decorator arguments, include & exclude, are used to control whether
    a request is logged or not. By default all requests are logged, but if you
    wish to have fine-grained control over the logging, this is where to do it.

    For instance, if you want to ignore all staff user requests:

        @log_request(exclude=lambda r: r.user.is_staff)
        def view(request):
            pass

    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def inner_func(
            request: HttpRequest, *args: object, **kwargs: object
        ) -> HttpResponse:
            with Timer() as t:
                response = func(request, *args, **kwargs)
            duration = t.duration
            if not include(request):
                return response
            if exclude(request):
                return response
            try:
                RequestLog.objects.create(
                    request=request,
                    response=response,
                    duration=duration,
                )
            except Exception:  # noqa: B902
                logger.exception("Error storing RequestLog.")
            return response

        return inner_func

    return decorator
