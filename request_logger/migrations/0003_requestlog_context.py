# Generated by Django 4.0.3 on 2022-03-07 17:52

import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("request_logger", "0002_alter_requestlog_response_class"),
    ]

    operations = [
        migrations.AddField(
            model_name="requestlog",
            name="context",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=django.core.serializers.json.DjangoJSONEncoder,
                help_text="Customisable JSON extracted from the request using REQUEST_LOGGER_CONTEXT_EXTRACTOR",
            ),
        ),
    ]
