import logging

from typing import Any
from django.core.management import BaseCommand

from pyreydenx import Client as RxClient
from pyreydenx.order import Order as RxOrder
from pyreydenx.action import Action
from pyreydenx.model.task import TaskStatusChoices
from pyreydenx.exceptions import NotFoundError

from core.models import Task, Order


class Command(BaseCommand):
    help = ""
    requires_migrations_checks = True

    def handle(self, *args: Any, **options: Any) -> str | None:
        client = RxClient()

        for task in Task.objects.filter(status=TaskStatusChoices.PENDING):
            try:
                result = Action.status(
                    client=client, order_id=task.order_id, task_id=task.external_id
                )
            except NotFoundError:
                task.error(TaskStatusChoices.ERROR)
                continue

            match result.status:
                case TaskStatusChoices.PENDING | TaskStatusChoices.IN_PROGRESS:
                    logging.debug(f"{task}: Status: {result.status} - SKIPPED")
                case TaskStatusChoices.ERROR | TaskStatusChoices.ACTION_REQUIRED:
                    logging.error(f"{task}: Status: {result.status}")
                    task.error(result.status)
                case TaskStatusChoices.COMPLETED:
                    order_id = 0
                    if isinstance(result.details, dict):
                        order_id = int(result.details.get("message", task.order_id))
                    else:
                        order_id = task.order_id

                    if order_id > 0:
                        if task.complete(order_id):
                            logging.info(f"{task}: Completed")

                            try:
                                order_source = RxOrder.details(client, order_id)
                                if order_source:
                                    model = Order.objects.get(
                                        external_id=order_id,
                                        platform=order_source.result.platform,
                                    )
                                    model.sync(order_source.result)
                                    if model.user != task.user:
                                        model.user = task.user
                                        model.save(update_fields=["user"])
                            except Order.DoesNotExist:
                                if model := Order.make_from_source(order_source.result):
                                    logging.info(f"{task}: New Order created ({model})")
                                    if model.user != task.user:
                                        model.user = task.user
                                        model.save(update_fields=["user"])
                            except Exception:
                                pass
                        else:
                            logging.error(f"{task}: Failed to change status")
                    else:
                        logging.error(f"{task}: Unknown Order ID")
                case _:
                    logging.warning(f"{task}: Unknown Status")
