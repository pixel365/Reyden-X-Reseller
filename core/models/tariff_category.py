from datetime import datetime, timezone
from django.db import models
from django.contrib import admin
from django.http import HttpRequest

from typing import Self

from pyreydenx.model.price_category import PriceCategory


class TariffCategory(models.Model):
    name = models.CharField(max_length=128, verbose_name="Name")
    description = models.TextField(blank=True, verbose_name="Description")
    external_id = models.IntegerField(default=0, editable=False)
    is_active = models.BooleanField(default=True, editable=False)
    source = models.TextField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    synchronized_at = models.DateTimeField(default=None, blank=True, editable=False)

    class Meta:
        verbose_name = "price category"
        verbose_name_plural = "price categories"
        ordering = ["-external_id"]
        indexes = [
            models.Index(fields=["external_id"]),
        ]

    def __str__(self) -> str:
        return self.name

    def sync(self, external_model: PriceCategory):
        self.refresh_from_db()
        update_fields = ["source", "synchronized_at"]

        self.source = external_model.model_dump_json()
        self.synchronized_at = datetime.now(tz=timezone.utc)

        if self.external_id != external_model.id:
            update_fields.append("external_id")
            self.external_id = external_model.id

        self.save(update_fields=update_fields)

    @staticmethod
    def make_from_source(external_model: PriceCategory, *args, **kwargs) -> Self | None:
        model = TariffCategory()
        model.name = external_model.name
        model.description = external_model.description
        model.external_id = external_model.id
        model.is_active = external_model.is_active
        model.source = external_model.model_dump_json()
        model.created_at = datetime.now(tz=timezone.utc)
        model.synchronized_at = model.created_at
        model.save()

        if model.pk:
            return model
        return None


class TariffCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = ("name",)

    def has_delete_permission(self, request: HttpRequest, obj=None):
        return False
