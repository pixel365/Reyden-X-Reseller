from typing import Any, Self
from django.db import models

from pyreydenx.model.site_stat import SiteStat


class DomainStats(models.Model):
    order = models.ForeignKey(to="core.Order", on_delete=models.CASCADE, editable=False)
    domain = models.CharField(max_length=256, editable=False)
    views = models.BigIntegerField(default=0, editable=False)
    clicks = models.BigIntegerField(default=0, editable=False)
    ctr = models.FloatField(default=0.0, editable=False)

    class Meta:
        unique_together = (
            "order",
            "domain",
        )
        indexes = [models.Index(fields=("order",))]

    @staticmethod
    def make_from_source(source: SiteStat, order: Any) -> Self | None:
        try:
            model = DomainStats.objects.get(order=order, domain=source.domain)
            model.views = source.views
            model.clicks = source.clicks
            model.ctr = source.ctr
            model.save(update_fields=["views", "clicks", "ctr"])
        except DomainStats.DoesNotExist:
            model = DomainStats()
            model.order = order
            model.domain = source.domain
            model.views = source.views
            model.clicks = source.clicks
            model.ctr = source.ctr
            model.save()

        if model.pk:
            return model
        return None
