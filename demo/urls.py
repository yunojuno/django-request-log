from django.contrib import admin
from django.urls import path
from django.views import debug

from . import views

admin.autodiscover()

urlpatterns = [
    path("", debug.default_urlconf),
    path("admin/", admin.site.urls),
    path("200/", views.http_200, name="200"),
    path("301/", views.http_301, name="301"),
    path("cbv/", views.DemoCBV.as_view(), name="cbv"),
    path("drf/", views.drf, name="drf"),
]
