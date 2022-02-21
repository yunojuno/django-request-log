from __future__ import annotations

from django.conf import settings
from django.http import HttpRequest


def _include(request: HttpRequest) -> bool:
    # default decorator 'include' argument - returns True to log all requests
    return True


def _exclude(request: HttpRequest) -> bool:
    # default decorator 'exclude' argument - returns False to exclude no requests
    return False


# Used to control logging at the project level.
DEFAULT_INCLUDE_FUNC = getattr(settings, "REQUEST_LOGGER_DEFAULT_INCLUDE", _include)
DEFAULT_EXCLUDE_FUNC = getattr(settings, "REQUEST_LOGGER_DEFAULT_EXCLUDE", _exclude)
