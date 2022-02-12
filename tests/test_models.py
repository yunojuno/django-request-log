from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.base import SessionBase
from django.http import HttpResponse, StreamingHttpResponse
from django.test import RequestFactory

from request_logger.models import RequestLog, parse_request, parse_response

User = get_user_model()


class TestParseRequest:
    def test_defaults(self, rf: RequestFactory) -> None:
        request = rf.get("/")
        assert parse_request(request) == {
            "http_method": "GET",
            "http_referer": "",
            "http_user_agent": "",
            "remote_addr": "127.0.0.1",
            "request_accepts": "",
            "request_content_type": "",
            "request_uri": "http://testserver/",
            "session_key": "",
        }

    def test_content_type(self, rf: RequestFactory) -> None:
        request = rf.get("/", CONTENT_TYPE="application/foo")
        assert parse_request(request)["request_content_type"] == "application/foo"

    def test_accepts(self, rf: RequestFactory) -> None:
        request = rf.get("/", HTTP_ACCEPT="application/foo")
        assert parse_request(request)["request_accepts"] == "application/foo"

    def test_user_agent(self, rf: RequestFactory) -> None:
        request = rf.get("/", HTTP_USER_AGENT="spyware 1.0")
        assert parse_request(request)["http_user_agent"] == "spyware 1.0"

    def test_referer(self, rf: RequestFactory) -> None:
        request = rf.get("/", HTTP_REFERER="/foo")
        assert parse_request(request)["http_referer"] == "/foo"

    def test_remote_addr__forwarded(self, rf: RequestFactory) -> None:
        request = rf.get("/", HTTP_X_FORWARDED_FOR="1.2.3.4", REMOTE_ADDR="4.3.2.1")
        assert parse_request(request)["remote_addr"] == "1.2.3.4"

    def test_remote_addr__not_forwarded(self, rf: RequestFactory) -> None:
        request = rf.get("/", REMOTE_ADDR="4.3.2.1")
        assert parse_request(request)["remote_addr"] == "4.3.2.1"

    def test_session(self, rf: RequestFactory) -> None:
        request = rf.get("/")
        request.session = mock.Mock(spec=SessionBase)
        assert parse_request(request)["session_key"] == request.session.session_key

    def test_session__missing(self, rf: RequestFactory) -> None:
        request = rf.get("/")
        assert parse_request(request)["session_key"] == ""

    def test_user__authenticated(self, rf: RequestFactory) -> None:
        request = rf.get("/")
        request.user = User()
        assert request.user.is_authenticated
        assert parse_request(request)["user"] == request.user

    def test_user__anonymous(self, rf: RequestFactory) -> None:
        request = rf.get("/")
        request.user = AnonymousUser()
        assert "user" not in parse_request(request)


class TestParseResponse:
    def test_defaults(self) -> None:
        response = HttpResponse()
        assert response.status_code == 200
        assert response.headers == {"Content-Type": "text/html; charset=utf-8"}
        assert parse_response(response) == {
            "content_length": 0,
            "http_status_code": response.status_code,
            "redirect_to": "",
            "response_content_type": response.headers["Content-Type"],
        }

    def test_redirect_to(self) -> None:
        response = HttpResponse()
        response.url = "/foo"
        assert parse_response(response)["redirect_to"] == "/foo"

    def test_streaming_response(self) -> None:
        response = StreamingHttpResponse()
        assert parse_response(response)["content_length"] is None


@pytest.mark.django_db
class TestRequestLogManager:
    def test_create__no_args(self) -> None:
        rl = RequestLog.objects.create()
        assert rl.user is None
        assert rl.reference == ""
        assert rl.session_key == ""
        assert rl.request_uri == ""
        assert rl.remote_addr == ""
        assert rl.http_method == ""
        assert rl.request_content_type == ""
        assert rl.request_accepts == ""
        assert rl.http_user_agent == ""
        assert rl.http_referer == ""
        assert rl.http_status_code is None
        assert rl.content_length is None
        assert rl.response_content_type == ""
        assert rl.redirect_to == ""
        assert rl.duration is None
        assert rl.timestamp is not None

    def test_create__request_only(self, rf: RequestFactory) -> None:
        request = rf.get("/")
        rl = RequestLog.objects.create(request)
        assert rl.user is None
        assert rl.reference == ""
        assert rl.session_key == ""
        assert rl.request_uri == "http://testserver/"
        assert rl.remote_addr == "127.0.0.1"
        assert rl.http_method == "GET"
        assert rl.request_content_type == ""
        assert rl.request_accepts == ""
        assert rl.http_user_agent == ""
        assert rl.http_referer == ""
        assert rl.http_status_code is None
        assert rl.content_length is None
        assert rl.response_content_type == ""
        assert rl.redirect_to == ""
        assert rl.duration is None
        assert rl.timestamp is not None

    def test_create__request_response(self, rf: RequestFactory) -> None:
        request = rf.get("/")
        response = HttpResponse()
        rl = RequestLog.objects.create(request=request, response=response)
        assert rl.user is None
        assert rl.reference == ""
        assert rl.session_key == ""
        assert rl.request_uri == "http://testserver/"
        assert rl.remote_addr == "127.0.0.1"
        assert rl.http_method == "GET"
        assert rl.request_content_type == ""
        assert rl.request_accepts == ""
        assert rl.http_user_agent == ""
        assert rl.http_referer == ""
        assert rl.http_status_code == 200
        assert rl.content_length == 0
        assert rl.response_content_type == "text/html; charset=utf-8"
        assert rl.redirect_to == ""
        assert rl.duration is None
        assert rl.timestamp is not None

    def test_create__reference(self, rf: RequestFactory) -> None:
        rl = RequestLog.objects.create(reference="foo")
        assert rl.reference == "foo"

    def test_create__duration(self) -> None:
        rl = RequestLog.objects.create(duration=0.123)
        assert rl.duration == 0.123


class TestModelProperties:
    @pytest.mark.parametrize(
        "request_uri, scheme, netloc, hostname, path, query",
        [
            ("http://google.com/foo", "http", "google.com", "google.com", "/foo", ""),
            (
                "http://google.com:80/foo",
                "http",
                "google.com:80",
                "google.com",
                "/foo",
                "",
            ),
            (
                "http://google.com:80/foo?q=bar",
                "http",
                "google.com:80",
                "google.com",
                "/foo",
                "q=bar",
            ),
        ],
    )
    def test_url_components(
        self, request_uri, scheme, netloc, hostname, path, query
    ) -> None:
        rl = RequestLog(request_uri=request_uri)
        assert rl.scheme == scheme
        assert rl.netloc == netloc
        assert rl.hostname == hostname
        assert rl.path == path
        assert rl.query == query

    @pytest.mark.parametrize(
        "id,method,url,status_code,expected",
        [
            (None, "GET", "", None, "GET"),
            (1, "GET", "http://google.com", 200, "[200] GET"),
            (1, "GET", "http://google.com/foo", 200, "[200] GET /foo"),
        ],
    )
    def test_str(
        self,
        id: int | None,
        method: str,
        url: str,
        status_code: int | None,
        expected: str,
    ) -> None:
        rl = RequestLog(
            id=id,
            http_method=method,
            request_uri=url,
            http_status_code=status_code,
        )
        assert str(rl) == expected

    @pytest.mark.parametrize(
        "id,method,url,status_code,user_id,expected",
        [
            (
                None,
                "GET",
                "",
                None,
                None,
                "<RequestLog id=None method='GET' status_code=None path='' user=None>",
            ),
            (
                1,
                "GET",
                "http://google.com",
                200,
                None,
                "<RequestLog id=1 method='GET' status_code=200 path='' user=None>",
            ),
            (
                1,
                "GET",
                "http://google.com/foo",
                200,
                1,
                "<RequestLog id=1 method='GET' status_code=200 path='/foo' user=1>",
            ),
        ],
    )
    def test_repr(
        self,
        id: int | None,
        method: str,
        url: str,
        status_code: int | None,
        user_id: int | None,
        expected: str,
    ) -> None:
        rl = RequestLog(
            id=id,
            http_method=method,
            request_uri=url,
            http_status_code=status_code,
            user_id=user_id,
        )
        assert repr(rl) == expected
