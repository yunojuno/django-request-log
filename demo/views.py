from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from request_logger.decorators import log_request, log_request_method


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


@log_request(lambda r: r.user.username)
def _cbv(request: HttpRequest) -> HttpResponse:
    return HttpResponse("OK")


class DemoCBV(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return _cbv(request)
