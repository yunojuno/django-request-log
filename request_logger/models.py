from __future__ import annotations

from typing import TypeAlias

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.http import HttpRequest
from django.utils.timezone import now as tz_now
from django.utils.translation import gettext_lazy as _lazy

# TODO: work out how to get this to work with get_user_model | AUTH_USER_MODEL
User: TypeAlias = AbstractUser

RequestKwargs: TypeAlias = dict[str, str | User | None]


def parse_request(request: HttpRequest) -> RequestKwargs:
    """Extract values from HttpRequest."""
    kwargs: RequestKwargs = {}
    kwargs["http_method"] = request.method
    kwargs["request_uri"] = request.path
    kwargs["query_string"] = request.META.get("QUERY_STRING", "")
    kwargs["http_user_agent"] = request.META.get("HTTP_USER_AGENT", "")[:400]
    # we care about the domain more than the URL itself, so truncating
    # doesn't lose much useful information
    kwargs["http_referer"] = request.META.get("HTTP_REFERER", "")[:400]
    # X-Forwarded-For is used by convention when passing through
    # load balancers etc., as the REMOTE_ADDR is rewritten in transit
    kwargs["remote_addr"] = (
        request.META.get("HTTP_X_FORWARDED_FOR")
        if "HTTP_X_FORWARDED_FOR" in request.META
        else request.META.get("REMOTE_ADDR", "")
    )
    # these two require middleware, so may not exist
    if session := getattr(request, "session", None):
        kwargs["session_key"] = session.session_key or ""
    else:
        kwargs["session_key"] = ""
    # NB you can't store AnonymouseUsers, so don't bother trying
    if (user := getattr(request, "user", None)) and user.is_authenticated:
        kwargs["user"] = user
    return kwargs


class RequestLogManager(models.Manager):
    def create(
        self, request: HttpRequest | None = None, **kwargs: object
    ) -> RequestLog:
        if request:
            request_kwargs = parse_request(request)
            kwargs.update(request_kwargs)
        return super().create(**kwargs)


class RequestLogBase(models.Model):
    """Abstract base class for request logs."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    reference = models.CharField(
        max_length=100,
        help_text=_lazy(
            "General-purpose free text field - useful for classifying requests."
        ),
        db_index=True,
    )
    session_key = models.CharField(blank=True, default="", max_length=40)
    http_method = models.CharField(max_length=10)
    request_uri = models.URLField(verbose_name=_lazy("Request path"))
    query_string = models.CharField(max_length=1000, blank=True, default="")
    remote_addr = models.CharField(max_length=100, default="")
    http_user_agent = models.CharField(max_length=400, default="")
    http_referer = models.CharField(max_length=400, default="")
    duration = models.FloatField(
        blank=True, null=True, verbose_name=_lazy("Request duration (sec)")
    )
    # these are HttpResponse attributes, and will need to set manually
    response_status_code = models.IntegerField(
        blank=True,
        null=True,
        help_text=_lazy("Response HTTP status code (2xx, 3xx, 4xx, 5xx, etc)."),
    )
    response_content_length = models.IntegerField(
        null=True, blank=True, help_text=_lazy("Length of the response body in bytes.")
    )
    response_content_type = models.CharField(
        default="",
        max_length=100,
        blank=True,
        help_text=_lazy("Response Content-Type header."),
    )
    response_location = models.CharField(
        max_length=400,
        help_text=_lazy("Response location in the event of a redirect (3xx)."),
    )
    timestamp = models.DateTimeField(default=tz_now)

    objects: RequestLogManager = RequestLogManager()

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f"RequestLog #{self.pk}: '{self.request_uri}'"


class RequestLog(RequestLogBase):
    """Default concrete subclass of RequestLogBase."""
