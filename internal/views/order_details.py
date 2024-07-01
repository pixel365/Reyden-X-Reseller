import json
from typing import Any

from django.http import HttpRequest
from django.http.response import (
    HttpResponse as HttpResponse,
    HttpResponseForbidden,
    JsonResponse,
)
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.utils.translation import gettext_lazy as _

from core.mixins import LoginRequiredMixin
from core.models.domain_stats import DomainStats
from core.models.order import Order
from core.helpers import Perms, Platform
from core.models.payment import Payment

from pyreydenx import Client as RxClient
from pyreydenx.action import Action as RxAction
from pyreydenx.model.task import ActionResult

from core.models.task import Task


class OrderDetailsView(LoginRequiredMixin, DetailView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.template_name = "internal/pages/order_details.html"
        self.model = Order
        self.context_object_name = "order"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        perms: list[Perms] = []

        if self.object.platform == Platform.TWITCH:
            context["twitch_active"] = True
            perms = [Perms.CAN_VIEW_TWITCH_ORDERS, Perms.CAN_CREATE_TWITCH_ORDERS]

        if self.object.platform == Platform.YOUTUBE:
            context["youtube_active"] = True
            perms = [Perms.CAN_VIEW_YOUTUBE_ORDERS, Perms.CAN_CREATE_YOUTUBE_ORDERS]

        if not self.request.user.has_perms(perms):
            return HttpResponseForbidden()

        context["title"] = self.object
        context["breadcrumbs"] = [
            {
                "name": self.object.platform.capitalize() + " " + _("Orders"),
                "url": reverse_lazy(f"internal:{self.object.platform}"),
            },
            {"name": self.object, "url": None},
        ]
        context["domains"] = DomainStats.objects.filter(order=self.object)
        context["payments"] = Payment.objects.filter(order=self.object)

        return context

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super(OrderDetailsView, self).get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        client = RxClient()
        body = json.loads(request.body.decode())
        action = body.get("action", None)
        result = None

        match action:
            case "pay":
                pass
            case "run" | "cancel" | "stop" | "increase_off":
                result = RxAction.__dict__[action](
                    client, self.get_object().external_id
                )
            case (
                "change_online_value"
                | "change_increase_value"
                | "increase_on"
                | "add_views"
            ):
                try:
                    value = int(body.get("value", 0))
                    if value > 0:
                        result = RxAction.__dict__[action](
                            client, self.get_object().external_id, value
                        )
                except (ValueError, TypeError):
                    pass
            case _:
                result = None

        if isinstance(result, ActionResult):
            Task.make_from_source(request=request, source=result)
            return JsonResponse(status=200, data=result.task.model_dump())

        return JsonResponse(status=403, data={})
