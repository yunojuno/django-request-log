from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from request_logger.decorators import log_request


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")


@log_request(lambda r: r.user.username)
def http_200(request: HttpRequest) -> HttpResponse:
    return index(request)


@log_request(lambda r: r.user.username)
def http_301(request: HttpRequest) -> HttpResponseRedirect:
    return HttpResponseRedirect(reverse("200"))


@log_request("DRF")
@api_view(["GET"])
def drf(request: Request) -> Response:
    return Response(data={"result": "OK"})
