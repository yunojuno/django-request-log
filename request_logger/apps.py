from __future__ import annotations

from django.apps import AppConfig


class RequestLoggerAppConfig(AppConfig):
    name = "request_logger"
    verbose_name = "HTTP Request logs"
