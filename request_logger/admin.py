from django.contrib import admin

from .models import RequestLog


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "reference",
        "http_method",
        "request_uri",
        "http_status_code",
        "duration",
    )
    readonly_fields = (
        "user",
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
    exclude = ("request_uri",)
