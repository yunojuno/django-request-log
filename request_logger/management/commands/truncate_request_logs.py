from __future__ import annotations

import datetime
from typing import cast

from django.core.management import BaseCommand
from django.core.management.base import CommandParser

from request_logger.models import RequestLog


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("-d", "--days", type=int, default=365, dest="days")
        return super().add_arguments(parser)

    def handle(self, *args: object, **options: object) -> str | None:
        days = cast(int, options["days"])
        min_date = datetime.date.today() - datetime.timedelta(days=days)
        logs = RequestLog.objects.filter(timestamp__date__lt=min_date)
        count = logs.count()
        self.stdout.write(f"Deleting records before {min_date}")
        self.stdout.write(f"Deleting {count} records")
        logs.delete()
        self.stdout.write(f"Deleted {count} records")
        return count
