from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from request_logger.decorators import log_request


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")


@log_request()
def http_200(request: HttpRequest) -> HttpResponse:
    return index(request)


@log_request()
def http_301(request: HttpRequest) -> HttpResponseRedirect:
    return HttpResponseRedirect(reverse("200"))


@log_request()
@api_view(["GET"])
def drf(request: Request) -> Response:
    return Response(data={"result": "OK"})


@log_request()
def _cbv(request: HttpRequest) -> HttpResponse:
    return HttpResponse("OK")


class DemoCBV(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return _cbv(request)
