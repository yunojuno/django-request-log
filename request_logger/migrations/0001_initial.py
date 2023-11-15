# Generated by Django 4.0.2 on 2022-02-21 10:45

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="RequestLog",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "source",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Class path of model used to log the request.",
                        max_length=200,
                    ),
                ),
                (
                    "view_func",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="View function path - taken from request.resolver_match._func_path",
                        max_length=200,
                    ),
                ),
                (
                    "session_key",
                    models.CharField(blank=True, default="", max_length=40),
                ),
                (
                    "request_uri",
                    models.URLField(
                        help_text="Request URI from HttpRequest.build_absolute_uri()"
                    ),
                ),
                ("remote_addr", models.CharField(default="", max_length=100)),
                ("http_method", models.CharField(max_length=10)),
                ("request_content_type", models.CharField(default="", max_length=100)),
                (
                    "request_accepts",
                    models.CharField(
                        default="",
                        help_text="HTTP 'Accept' header value.",
                        max_length=200,
                    ),
                ),
                ("http_user_agent", models.CharField(default="", max_length=400)),
                ("http_referer", models.CharField(default="", max_length=400)),
                (
                    "http_status_code",
                    models.IntegerField(
                        blank=True, null=True, verbose_name="Response status code"
                    ),
                ),
                (
                    "content_length",
                    models.IntegerField(
                        blank=True,
                        help_text="Length of the response body in bytes.",
                        null=True,
                    ),
                ),
                ("response_class", models.CharField(default="", max_length=50)),
                (
                    "response_content_type",
                    models.CharField(blank=True, default="", max_length=100),
                ),
                (
                    "redirect_to",
                    models.CharField(
                        help_text="Response location in the event of a redirect (3xx).",
                        max_length=400,
                    ),
                ),
                (
                    "duration",
                    models.FloatField(
                        blank=True, null=True, verbose_name="Request duration (sec)"
                    ),
                ),
                ("timestamp", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
