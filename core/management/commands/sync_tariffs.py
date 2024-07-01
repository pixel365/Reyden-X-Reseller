import logging

from typing import Any
from django.core.management import BaseCommand
from django.core.management.base import CommandParser

from pyreydenx import Client as RxClient
from pyreydenx.prices import Prices
from core.helpers import Platform
from core.models.tariff import Tariff
from core.models.tariff_category import TariffCategory


class Command(BaseCommand):
    help = ""
    requires_migrations_checks = True

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--platform", type=Platform)

    def handle(self, *args: Any, **options: Any) -> str | None:
        platform = options.get("platform")
        if platform not in Platform.enabled_platforms():
            logging.error(f"Not Implemented for '{platform}'")
            return None

        client = RxClient()

        categories = Prices.get_categories(client=client)
        for c in categories.result:
            try:
                model = TariffCategory.objects.get(external_id=c.id)
                model.sync(external_model=c)
            except TariffCategory.DoesNotExist:
                TariffCategory.make_from_source(external_model=c)

        next = True
        while next:
            result = Prices.get_prices(client=client, platform=platform)
            next = result.has_next

            for price in result.result:
                try:
                    model = Tariff.objects.get(external_id=price.id, platform=platform)
                    model.sync(source=price)
                    logging.info(f"{model}: Synchronization completed")
                except Tariff.DoesNotExist:
                    if model := Tariff.make_from_source(
                        source=price, platform=platform
                    ):
                        logging.info(f"{model}: Synchronization completed")
                    else:
                        logging.error(
                            f"Synchronization failed! External Id: {price.id}"
                        )
