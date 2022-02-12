from django.contrib import admin

from .models import RequestLog


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    # pass
    list_display = (
        "id",
        "reference",
        "http_method",
        "request_uri",
        "response_status_code",
        "duration",
        "user",
    )
    readonly_fields = (
        "timestamp",
        "session_key",
        "http_method",
        "request_uri",
        "query_string",
        "remote_addr",
        "http_referer",
        "http_user_agent",
        "duration",
        "response_status_code",
        "response_content_length",
        "response_location",
    )
