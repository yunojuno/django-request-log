from __future__ import annotations

import logging
from functools import wraps
from types import TracebackType
from typing import Callable, TypeAlias

from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.utils import timezone

from request_logger.models import RequestLog

logger = logging.getLogger(__name__)

# if the reference arg is not a fixed str, it must be a callable
ReferenceFunc: TypeAlias = Callable[[HttpRequest], str]
# functions used to filter in/out request to log
RequestFilterFunc: TypeAlias = Callable[[HttpRequest], bool]


class Timer(object):
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


def _include(request: HttpRequest) -> bool:
    # default decorator 'include' argument - returns True to log all requests
    return True


def _exclude(request: HttpRequest) -> bool:
    # default decorator 'exclude' argument - returns False to exclude no requests
    return False


@transaction.atomic
def log_request(
    include: RequestFilterFunc = _include, exclude: RequestFilterFunc = _exclude
) -> Callable:
    """Decorate view function to log a request-response."""

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
