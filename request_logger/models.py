from __future__ import annotations

from typing import TypeAlias
from urllib.parse import ParseResult, urlparse

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.http import HttpRequest, HttpResponse, StreamingHttpResponse
from django.utils.timezone import now as tz_now
from django.utils.translation import gettext_lazy as _lazy

# TODO: work out how to get this to work with get_user_model | AUTH_USER_MODEL
User: TypeAlias = AbstractUser

RequestKwargs: TypeAlias = dict[str, str | User | None]
ResponseKwargs: TypeAlias = dict[str, str | int | None]


def parse_request(request: HttpRequest) -> RequestKwargs:
    """Extract values from HttpRequest."""
    kwargs: RequestKwargs = {}
    kwargs["request_uri"] = request.build_absolute_uri()
    kwargs["http_method"] = request.method
    kwargs["request_content_type"] = request.content_type
    kwargs["request_accepts"] = request.headers.get("accept", "")[:200]
    kwargs["http_user_agent"] = request.META.get("HTTP_USER_AGENT", "")[:400]
    kwargs["http_referer"] = request.META.get("HTTP_REFERER", "")[:400]
    # X-Forwarded-For is used by convention when passing through
    # load balancers etc., as the REMOTE_ADDR is rewritten in transit
    kwargs["remote_addr"] = (
        request.META.get("HTTP_X_FORWARDED_FOR")
        if "HTTP_X_FORWARDED_FOR" in request.META
        else request.META.get("REMOTE_ADDR", "")
    )
    if session := getattr(request, "session", None):
        kwargs["session_key"] = session.session_key or ""
    else:
        kwargs["session_key"] = ""
    # NB you can't store AnonymouseUsers, so don't bother trying
    if hasattr(request, "user") and request.user.is_authenticated:
        kwargs["user"] = request.user
    return kwargs


def parse_response(response: HttpResponse) -> ResponseKwargs:
    """Extract values from HttpResponse."""
    kwargs: ResponseKwargs = {}
    kwargs["http_status_code"] = response.status_code
    kwargs["redirect_to"] = getattr(response, "url", "")
    if isinstance(response, StreamingHttpResponse):
        kwargs["content_length"] = None
    else:
        kwargs["content_length"] = len(response.content)
    kwargs["response_content_type"] = response.headers.get("Content-Type", "")
    return kwargs


class RequestLogManager(models.Manager):
    def create(
        self,
        request: HttpRequest | None = None,
        response: HttpResponse | None = None,
        **kwargs: object,
    ) -> RequestLog:
        if request:
            kwargs.update(parse_request(request))
        if response:
            kwargs.update(parse_response(response))
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
    request_uri = models.URLField(
        help_text=_lazy("Request URI from HttpRequest.build_absolute_uri()")
    )
    remote_addr = models.CharField(max_length=100, default="")
    http_method = models.CharField(max_length=10)
    request_content_type = models.CharField(max_length=100, default="")
    request_accepts = models.CharField(
        max_length=200, default="", help_text=_lazy("HTTP 'Accept' header value.")
    )
    http_user_agent = models.CharField(max_length=400, default="")
    http_referer = models.CharField(max_length=400, default="")
    http_status_code = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_lazy("Response status code"),
    )
    content_length = models.IntegerField(
        null=True, blank=True, help_text=_lazy("Length of the response body in bytes.")
    )
    response_content_type = models.CharField(
        default="",
        max_length=100,
        blank=True,
    )
    redirect_to = models.CharField(
        max_length=400,
        help_text=_lazy("Response location in the event of a redirect (3xx)."),
    )
    duration = models.FloatField(
        blank=True, null=True, verbose_name=_lazy("Request duration (sec)")
    )
    timestamp = models.DateTimeField(default=tz_now)

    objects: RequestLogManager = RequestLogManager()

    class Meta:
        abstract = True

    def __str__(self) -> str:
        if self.http_status_code:
            return f"[{self.http_status_code}] {self.http_method} {self.path}".strip()
        return f"{self.http_method} {self.path}".strip()

    def __repr__(self) -> str:
        return (
            f"<RequestLog id={self.id} method='{self.http_method}' "
            f"status_code={self.http_status_code} "
            f"path='{self.path}' user={self.user_id}>"
        )

    @property
    def url_components(self) -> ParseResult:
        return urlparse(self.request_uri)

    @property
    def scheme(self) -> str:
        return self.url_components.scheme

    @property
    def netloc(self) -> str:
        return self.url_components.netloc

    @property
    def hostname(self) -> str:
        return self.url_components.hostname or ""

    @property
    def path(self) -> str:
        return self.url_components.path

    @property
    def query(self) -> str:
        return self.url_components.query


class RequestLog(RequestLogBase):
    """Default concrete subclass of RequestLogBase."""
