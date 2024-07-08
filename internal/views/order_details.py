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
from django.core.exceptions import PermissionDenied

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
        user = self.request.user
        is_superuser = user.is_superuser
        can_edit = is_superuser or self.object.user == user
        can_view = is_superuser or self.object.user == user

        edit_perms: list[Perms] = []
        view_perms: list[Perms] = []

        if self.object.platform == Platform.TWITCH:
            context["twitch_active"] = True
            edit_perms = [
                Perms.CAN_EDIT_OTHER_TWITCH_ORDERS,
            ]
            view_perms = [
                Perms.CAN_VIEW_OTHER_TWITCH_ORDERS,
            ]

        if self.object.platform == Platform.YOUTUBE:
            context["youtube_active"] = True
            edit_perms = [
                Perms.CAN_EDIT_OTHER_YOUTUBE_ORDERS,
            ]
            view_perms = [
                Perms.CAN_VIEW_OTHER_YOUTUBE_ORDERS,
            ]

        can_view = can_view or user.has_perms(view_perms)
        can_edit = can_edit or user.has_perms(edit_perms)

        if not can_view:
            if not can_edit:
                raise PermissionDenied

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
        context["can_view"] = can_view
        context["can_edit"] = can_edit

        return context

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super(OrderDetailsView, self).get(request, *args, **kwargs)

    def post(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> JsonResponse | HttpResponseForbidden:
        user = self.request.user
        is_superuser = user.is_superuser
        can_edit = is_superuser or self.object.user == user

        if not can_edit:
            edit_perms: list[Perms] = []
            if self.object.platform == Platform.TWITCH:
                edit_perms = [
                    Perms.CAN_EDIT_OTHER_TWITCH_ORDERS,
                ]

            if self.object.platform == Platform.YOUTUBE:
                edit_perms = [
                    Perms.CAN_EDIT_OTHER_YOUTUBE_ORDERS,
                ]

            if not user.has_perms(edit_perms):
                return HttpResponseForbidden()

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
