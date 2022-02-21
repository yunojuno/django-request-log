from __future__ import annotations

from django.contrib import admin

from request_logger.models import RequestLog


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "http_method",
        "request_uri",
        "http_status_code",
        "duration",
        "source",
        "timestamp",
    )
    readonly_fields = (
        "user",
        "source",
        "view_func",
        "timestamp",
        "session_key",
        "http_method",
        "hostname",
        "path",
        "query",
        "remote_addr",
        "http_referer",
        "http_user_agent",
        "request_accepts",
        "request_content_type",
        "response_content_type",
        "response_class",
        "http_status_code",
        "content_length",
        "redirect_to",
        "duration",
    )
    list_filter = (
        "source",
        "timestamp",
    )
    exclude = ("request_uri",)
