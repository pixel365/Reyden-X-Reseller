from datetime import datetime, timezone
import json
from typing import Self
from django.db import models
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.http import HttpRequest

from pyreydenx.model.price import Price as RxPriceModel

from core.helpers import Platform
from .sync import AbstractSyncModel


class Tariff(AbstractSyncModel):
    _details = None
    _details_cache = False

    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    name = models.CharField(max_length=256, verbose_name="Name")
    description = models.TextField(verbose_name="Description")
    value = models.FloatField(default=0.0, verbose_name="Value")
    category = models.ForeignKey(
        to="core.TariffCategory",
        on_delete=models.CASCADE,
        null=True,
        default=None,
        editable=False,
    )
    external_value = models.FloatField(editable=False)
    source = models.TextField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    synchronized_at = models.DateTimeField(default=None, blank=True, editable=False)

    class Meta:
        verbose_name = "tariff"
        verbose_name_plural = "tariffs"
        ordering = ["-external_id"]
        indexes = [
            models.Index(
                fields=(
                    "external_id",
                    "platform",
                )
            )
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def details(self) -> RxPriceModel | None:
        if self._details_cache:
            return self._details

        if len(self.source):
            self._details_cache = True
            self._details = RxPriceModel(**json.loads(self.source))

        return self._details

    @staticmethod
    def make_from_source(source: RxPriceModel, *args, **kwargs) -> Self | None:
        if "platform" not in kwargs:
            return None

        from core.models.tariff_category import TariffCategory

        model = Tariff()
        model.name = source.name
        model.description = source.description
        model.external_value = source.price
        model.category = TariffCategory.objects.get(external_id=source.category_id)
        model.external_id = source.id
        model.platform = kwargs["platform"]
        model.source = source.model_dump_json()
        model.created_at = datetime.now(tz=timezone.utc)
        model.synchronized_at = model.created_at
        model.save()

        if model.pk:
            return model
        return None

    def sync(self, source: RxPriceModel):
        self.refresh_from_db()
        update_fields = ["source", "synchronized_at"]

        self.source = source.model_dump_json()
        self.synchronized_at = datetime.now(tz=timezone.utc)

        if self.external_id != source.id:
            update_fields.append("external_id")
            self.external_id = source.id

        self.save(update_fields=update_fields)

    @property
    def details(self) -> RxPriceModel | None:
        if len(self.source):
            return RxPriceModel(**json.loads(self.source))
        return None

    def clean_fields(self, *args, **kwargs) -> None:
        if (
            self.external_id < 0
            or len(self.source) < 1
            or self.platform
            not in (
                Platform.TWITCH,
                Platform.YOUTUBE,
            )
        ):
            raise ValidationError(message="Manually adding prices is prohibited")

    def save(self, *args, **kwargs) -> None:
        return super(Tariff, self).save(*args, **kwargs)


class TariffAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "is_active",
        "name",
        "category",
        "platform",
        "value",
        "external_value",
        "external_id",
        "synchronized_at",
    )
    list_filter = (
        "is_active",
        "platform",
    )
    exclude = ()

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        return False
