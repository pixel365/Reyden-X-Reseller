from datetime import datetime, timezone
import json
from typing import Self
from django.db import models
from django.contrib import admin
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _


from pyreydenx.order import OrderModel as RxOrderModel

from core.helpers import AvailableActon, OrderStatus, Platform

from .sync import AbstractSyncModel


class Order(AbstractSyncModel):
    _details = None
    _details_cache = False

    user = models.ForeignKey(
        to="core.User", on_delete=models.CASCADE, verbose_name="User"
    )
    tariff = models.ForeignKey(
        to="core.Tariff", on_delete=models.DO_NOTHING, editable=False
    )
    status = models.CharField(default="not_synchronized", max_length=50, editable=False)
    platform = models.CharField(max_length=50, editable=False)
    source = models.TextField(blank=True, editable=False)
    channel_search_content = models.CharField(
        default="", max_length=128, editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    synchronized_at = models.DateTimeField(default=None, blank=True, editable=False)

    class Meta:
        verbose_name = "order"
        verbose_name_plural = "orders"
        ordering = ["-external_id"]
        indexes = [
            models.Index(fields=("user",)),
            models.Index(fields=("external_id",)),
            models.Index(
                fields=(
                    "platform",
                    "status",
                )
            ),
        ]

    def __str__(self) -> str:
        return f"{__class__.__name__} #{self.external_id}"

    def __repr__(self) -> str:
        return f"<{__class__.__name__} #{self.external_id}: {self.status}>"

    @property
    def real_created_at(self) -> datetime:
        if self.external_id == 0:
            return self.created_at
        return self.details.created_at

    @property
    def cost(self) -> float:
        if self.external_id == 0:
            return 0.0
        return round(self.details.ordered_view_qty * self.tariff.external_value, 2)

    @property
    def ordered_views(self) -> int:
        return self.details.ordered_view_qty

    @property
    def viewers(self) -> int:
        return self.details.online_users_limit

    @property
    def views(self) -> int:
        if self.details.statistics:
            return self.details.statistics.views
        return 0

    @property
    def clicks(self) -> int:
        if self.details.statistics:
            return self.details.statistics.clicks
        return 0

    @property
    def ctr(self) -> float:
        if self.details.statistics:
            return self.details.statistics.ctr
        return 0.0

    @property
    def average_online(self) -> float:
        if self.details.statistics:
            return self.details.statistics.average.online
        return 0.0

    @property
    def views_balance(self) -> int:
        return self.details.ordered_view_qty - self.views

    @property
    def money_balance(self) -> float:
        return round(self.views_balance * self.tariff.external_value, 2)

    @property
    def complete(self) -> float:
        return round(self.views / self.ordered_views * 100, 2)

    @property
    def progress(self) -> float:
        return round(self.views / self.details.ordered_view_qty * 100, 2)

    @property
    def progress_color(self) -> str:
        progress = self.progress
        if progress <= 50:
            return "success"
        if 50 < progress <= 90:
            return "warning"
        return "danger"

    @property
    def details(self) -> RxOrderModel | None:
        if self._details_cache:
            return self._details

        if len(self.source):
            self._details_cache = True
            self._details = RxOrderModel(**json.loads(self.source))

        return self._details

    @property
    def status_badge(self) -> str:
        match self.status:
            case OrderStatus.ACTIVE:
                color = "success"
            case OrderStatus.CLOSED:
                color = "secondary"
            case (
                OrderStatus.NOT_STARTED
                | OrderStatus.NOT_PAID
                | OrderStatus.REJECTED
                | OrderStatus.ERROR
            ):
                color = "danger"
            case (
                OrderStatus.OFFLINE
                | OrderStatus.ONLINE_LIMIT
                | OrderStatus.WAITING
                | OrderStatus.DELAY
                | OrderStatus.SUSPENDED
            ):
                color = "warning"
            case OrderStatus.STOPPED | OrderStatus.CANCELED | OrderStatus.PAID:
                color = "primary"
            case _:
                color = "info"

        return f'<span class="badge bg-label-{color}">{self.status.upper()}</span>'

    @property
    def is_twitch(self) -> bool:
        return self.details.platform == Platform.TWITCH

    @property
    def is_youtube(self) -> bool:
        return self.details.platform == Platform.YOUTUBE

    @property
    def channel_image(self) -> str:
        extras = self.details.extras
        if not extras:
            return ""

        return extras.get("image_url", "")

    @property
    def channel_url(self) -> str:
        extras = self.details.extras
        if not extras:
            return ""

        if self.is_twitch:
            return f"https://twitch.tv/{extras.get("twitch_channel", "")}"

        if self.is_youtube:
            return f"https://www.youtube.com/channel/{extras.get("youtube_channel_id", "")}"

        return ""

    @property
    def channel_id(self) -> str | int:
        extras = self.details.extras
        if not extras:
            return ""

        if self.is_twitch:
            return extras.get("twitch_id", 0)

        if self.is_youtube:
            return extras.get("youtube_channel_id", "")

        return ""

    @property
    def channel_title(self) -> str:
        extras = self.details.extras
        if not extras:
            return ""

        if self.is_twitch:
            if extras.get("game_name", None):
                return extras["game_name"]
            else:
                return extras.get("twitch_channel", "")

        if self.is_youtube:
            return extras.get("youtube_channel_title", "")

        return ""

    @property
    def is_active(self) -> bool:
        return self.status == OrderStatus.ACTIVE

    @property
    def is_rejected(self) -> bool:
        return self.status == OrderStatus.REJECTED

    @property
    def is_stopped(self) -> bool:
        return self.status == OrderStatus.STOPPED

    @property
    def is_not_started(self) -> bool:
        return self.status == OrderStatus.NOT_STARTED

    @property
    def is_waiting(self) -> bool:
        return self.status == OrderStatus.WAITING

    @property
    def is_delay(self) -> bool:
        return self.status == OrderStatus.DELAY

    @property
    def is_offline(self) -> bool:
        return self.status == OrderStatus.OFFLINE

    @property
    def is_cancelled(self) -> bool:
        return self.status == OrderStatus.CANCELED

    @property
    def is_not_paid(self) -> bool:
        return self.status == OrderStatus.NOT_PAID

    @property
    def is_payed(self) -> bool:
        return self.status == OrderStatus.PAID

    @property
    def is_closed(self) -> bool:
        return self.status == OrderStatus.CLOSED

    @property
    def is_online_reached(self) -> bool:
        return self.status == OrderStatus.ONLINE_LIMIT_IS_REACHED

    @property
    def is_error(self) -> bool:
        return self.status == OrderStatus.ERROR

    @property
    def is_suspended(self) -> bool:
        return self.status == OrderStatus.SUSPENDED

    @property
    def is_not_syncronized(self) -> bool:
        return self.status == OrderStatus.NOT_SYNCHRONIZED

    @property
    def can_cancel(self) -> bool:
        return all(
            (
                not self.is_not_syncronized,
                not self.is_closed,
                not self.is_cancelled,
            )
        )

    @property
    def available_action(self) -> AvailableActon | None:
        if self.is_not_started:
            return AvailableActon(
                action="run",
                color="success",
                text=_("Run"),
            )

        if self.is_stopped:
            return AvailableActon(
                action="pay",
                color="primary",
                text=_("Pay"),
            )

        if all(
            (
                not self.is_closed,
                not self.is_rejected,
                not self.is_cancelled,
                not self.is_not_paid,
                not self.is_payed,
                not self.is_not_started,
                not self.is_stopped,
            )
        ):
            return AvailableActon(
                action="stop",
                color="danger",
                text=_("Stop"),
            )

        return None

    @staticmethod
    def make_from_source(source: RxOrderModel, *args, **kwargs) -> Self | None:
        from core.models import User, Tariff

        try:
            user = User.objects.filter(is_active=True, is_superuser=True)[0]
            tariff = Tariff.objects.filter(external_id=source.tariff_id)[0]
        except IndexError:
            return None

        model = Order()
        model.user = user
        model.tariff = tariff
        model.external_id = source.id
        model.status = source.status
        model.platform = source.platform
        model.source = source.model_dump_json()
        model.created_at = datetime.now(tz=timezone.utc)
        model.synchronized_at = model.created_at

        if source.extras:
            if source.platform == Platform.TWITCH and "twitch_channel" in source.extras:
                model.channel_search_content = source.extras["twitch_channel"].lower()

            if (
                source.platform == Platform.YOUTUBE
                and "youtube_channel_title" in source.extras
            ):
                model.channel_search_content = source.extras[
                    "youtube_channel_title"
                ].lower()

        model.save()

        if model.pk:
            return model
        return None

    def sync(self, source: RxOrderModel):
        self.refresh_from_db()
        update_fields = ["source", "synchronized_at"]

        self.source = source.model_dump_json()
        self.synchronized_at = datetime.now(tz=timezone.utc)

        if self.external_id != source.id:
            update_fields.append("external_id")
            self.external_id = source.id

        if self.status != source.status:
            update_fields.append("status")
            self.status = source.status

        self.save(update_fields=update_fields)


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "real_created_at",
        "user",
        "status",
        "platform",
        "external_id",
        "tariff",
        "synchronized_at",
    )
    list_filter = (
        "status",
        "platform",
    )
    exclude = ()

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    @admin.display(description="created at")
    def real_created_at(self, obj: Order):
        return obj.real_created_at
