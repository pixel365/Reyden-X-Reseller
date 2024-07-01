from datetime import datetime, timezone
from typing import Self
from django.db import models
from django.core.exceptions import ValidationError

from pyreydenx.model.user import Balance as RxBalance


class Balance(models.Model):
    amount = models.FloatField(default=0.0, editable=False)
    created_at = models.DateTimeField(auto_created=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def clean_fields(self, *args, **kwargs) -> None:
        q = Balance.objects.filter(pk__gt=0)[:1]
        if len(q):
            raise ValidationError("Already exists")

        return super().clean_fields(*args, **kwargs)

    @staticmethod
    def get_balance() -> Self | None:
        try:
            balance = Balance.objects.get(pk=1)
            return balance
        except Balance.DoesNotExist:
            pass
        return None

    @staticmethod
    def sync(source: RxBalance):
        balance = Balance.get_balance()
        if isinstance(balance, Balance):
            balance.amount = source.amount
            balance.save()
        else:
            model = Balance()
            model.created_at = datetime.now(tz=timezone.utc)
            model.amount = source.amount
            model.full_clean()
            model.save()
