from typing import Any
from django.core.management import BaseCommand
from django.core.management.base import CommandParser

from pyreydenx import Client as RxClient
from pyreydenx.user import User as RxUser
from core.helpers import Platform
from core.models.balance import Balance


class Command(BaseCommand):
    help = ""
    requires_migrations_checks = True

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--platform", type=Platform)

    def handle(self, *args: Any, **options: Any) -> str | None:
        client = RxClient()

        balance = RxUser.balance(client)
        if balance:
            Balance.sync(balance)
