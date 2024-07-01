import logging
from typing import Any
from django.core.management import BaseCommand
from django.core.management.base import CommandParser

from core.helpers import Platform
from core.models import Order

from pyreydenx import Client as RxClient
from pyreydenx.order import Order as RxOrder
from pyreydenx.model.order import Order as RxOrderModel

from core.models.domain_stats import DomainStats
from core.models.payment import Payment


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

        orders: list[RxOrderModel] = []
        client = RxClient()
        cursor, next = None, True
        while next:
            result = RxOrder.get_orders(client, cursor)
            cursor = result.cursor
            next = result.has_next

            for order in result.result:
                if order.platform != platform:
                    continue

                orders.append(order)

        if len(orders):
            for order in orders:
                model = None
                source = RxOrder.details(client=client, order_id=order.id)
                if not isinstance(source.result, RxOrderModel):
                    continue

                try:
                    model = Order.objects.get(
                        external_id=order.id, platform=order.platform
                    )
                    model.sync(source=source.result)
                except Order.DoesNotExist:
                    model = Order.make_from_source(source=source.result)

                if isinstance(model, Order):
                    paymentsCursor, paymentsNext = None, True
                    while paymentsNext:
                        paymentsResult = RxOrder.payments(
                            client=client, order_id=order.id, cursor=paymentsCursor
                        )
                        paymentsCursor = paymentsResult.cursor
                        paymentsNext = paymentsResult.has_next
                        for payment in paymentsResult.result:
                            Payment.make_from_source(source=payment, order=model)

                    domainStats = RxOrder.sites_stats(client=client, order_id=order.id)
                    for stat in domainStats.result:
                        DomainStats.make_from_source(source=stat, order=model)

                    logging.info(f"{model}: Synchronization completed")
                else:
                    logging.error(f"Synchronization failed! External Id: {order.id}")
