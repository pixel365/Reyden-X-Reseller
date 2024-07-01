from typing import Any, Self
from django.db import IntegrityError, models

from pyreydenx.model.payment import Payment as RxPayment


class Payment(models.Model):
    external_id = models.BigIntegerField(unique=True, editable=False)
    order = models.ForeignKey(to="core.Order", on_delete=models.CASCADE, editable=False)
    payed_at = models.DateTimeField(null=True, editable=False)
    amount = models.FloatField(editable=False)
    receipt = models.CharField(max_length=100, default="", editable=False)

    class Meta:
        ordering = ["-external_id"]
        indexes = [
            models.Index(fields=("external_id",)),
            models.Index(fields=("order",)),
        ]

    @property
    def views(self) -> int:
        return int(self.amount / self.order.tariff.external_value)

    @staticmethod
    def make_from_source(source: RxPayment, order: Any) -> Self | None:
        try:
            model = Payment()
            model.external_id = source.id
            model.order = order
            model.payed_at = source.payed_at
            model.amount = source.amount
            model.receipt = source.receipt
            model.save()

            if model.pk:
                return model
        except IntegrityError:
            pass

        return None
