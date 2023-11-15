from __future__ import annotations

from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory

from request_logger import decorators
from request_logger.models import RequestLog, RequestLogManager

User = get_user_model()


def view_func(request: HttpRequest) -> HttpResponse:
    return HttpResponse("OK")


@pytest.mark.django_db
class TestLogRequest:
    def test_log_request_reference(self, rf: RequestFactory) -> None:
        request = rf.get("/")
        func = decorators.log_request()(view_func)
        func(request)
        rl: RequestLog = RequestLog.objects.get()
        assert rl.source == "request_logger.RequestLog"
        assert rl.duration > 0.0

    def test_log_request_error(self, rf: RequestFactory) -> None:
        """Test that RequestLog error doesn't stop response."""
        request = rf.get("/")
        func = decorators.log_request()(view_func)
        with mock.patch.object(RequestLogManager, "create", side_effect=Exception):
            resp = func(request)
        assert resp.status_code == 200
        assert RequestLog.objects.count() == 0

    @pytest.mark.parametrize(
        "include,exclude,expected",
        [
            (lambda r: True, lambda r: False, 1),
            (lambda r: False, lambda r: False, 0),
            (lambda r: False, lambda r: True, 0),
            (lambda r: True, lambda r: True, 0),
        ],
    )
    def test_log_request_filters(
        self, rf: RequestFactory, include: bool, exclude: bool, expected: int
    ) -> None:
        """Test that RequestLog include/exclude function args."""
        request = rf.get("/")
        func = decorators.log_request(include=include, exclude=exclude)(view_func)
        resp = func(request)
        assert resp.status_code == 200
        assert RequestLog.objects.count() == expected
