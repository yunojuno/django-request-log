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
        func = decorators.log_request("foo")(view_func)
        func(request)
        rl: RequestLog = RequestLog.objects.get()
        assert rl.reference == "foo"
        assert rl.duration > 0.0

    def test_log_request_reference_func(self, rf: RequestFactory) -> None:
        """Test dynamic reference callable."""
        request = rf.get("/")
        request.user = User.objects.create(first_name="Fred")
        reference_func = lambda r: r.user.first_name
        func = decorators.log_request(reference_func)(view_func)
        func(request)
        # implicit assert that count == 1
        rl: RequestLog = RequestLog.objects.get()
        assert rl.reference == "Fred"
        assert rl.duration > 0.0

    def test_log_request_invalid_reference(self, rf: RequestFactory) -> None:
        """Test invalid reference value."""
        request = rf.get("/")
        request.user = User.objects.create(first_name="Fred")
        reference = request.user
        func = decorators.log_request(reference)(view_func)
        with pytest.raises(ValueError):
            func(request)

    def test_log_request_error(self, rf: RequestFactory) -> None:
        """Test that RequestLog error doesn't stop response."""
        request = rf.get("/")
        func = decorators.log_request("reference")(view_func)
        with mock.patch.object(RequestLogManager, "create", side_effect=Exception):
            resp = func(request)
        assert resp.status_code == 200
        assert RequestLog.objects.count() == 0
