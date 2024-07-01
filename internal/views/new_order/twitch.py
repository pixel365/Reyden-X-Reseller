import base64
from functools import partial
import json
from typing import Any

from django.http import HttpRequest, JsonResponse
from django.urls import reverse_lazy
from pydantic import ValidationError
from core.decorators import check_perms
from core.helpers import Perms, Platform
from core.mixins import LoginRequiredMixin
from core.models import Tariff
from core.models.task import Task
from core.utils import translated_description

from django.views.generic import TemplateView
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from pyreydenx.model.new_order_parameters import TwitchOrder
from pyreydenx.order import Order
from pyreydenx import Client
from pyreydenx.exceptions import (
    UnauthorizedError,
    UnknownError,
    NotFoundError,
    TooManyRequestsError,
)


_check_perms = partial(
    check_perms,
    perms=(Perms.CAN_CREATE_TWITCH_ORDERS,),
)


@method_decorator(_check_perms, name="dispatch")
class NewTwitch(LoginRequiredMixin, TemplateView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.template_name = "internal/pages/new_order.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> TemplateResponse:
        can_view_prices = request.user.has_perm(Perms.CAN_VIEW_PRICES)
        context = {
            "title": _("New Twitch Order"),
            "platform": Platform.TWITCH,
            "categories": "",
            "prices": "",
            "breadcrumbs": [
                {
                    "name": _("Twitch Orders"),
                    "url": reverse_lazy(f"internal:{Platform.TWITCH}"),
                },
                {"name": _("New Twitch Order"), "url": None},
            ],
        }

        uc = set()
        categories = []
        prices = []
        tariffs = (
            Tariff.objects.filter(is_active=True, platform=Platform.TWITCH)
            .select_related("category")
            .order_by("external_id")
        )

        for t in tariffs:
            if t.category.id not in uc:
                uc.add(t.category.id)
                categories.append(
                    {
                        "id": t.category.external_id,
                        "name": t.category.name,
                    }
                )
            prices.append(
                {
                    "id": t.external_id,
                    "name": t.name,
                    "category": t.category.external_id,
                    "price": t.details.price if can_view_prices else 0.0,
                    "views": t.details.views.model_dump(),
                    "viewers": t.details.online_viewers.model_dump(),
                    "description": translated_description(t.details.description),
                }
            )

        context["categories"] = base64.b64encode(
            json.dumps(categories).encode()
        ).decode()
        context["prices"] = base64.b64encode(json.dumps(prices).encode()).decode()

        return TemplateResponse(
            request=request, template=self.template_name, context=context
        )

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        try:
            parameters = TwitchOrder(**json.loads(request.body.decode()))
            client = Client()
            result = Order.create(client, parameters)
            task = Task.make_from_source(request, result)

            return JsonResponse(
                status=200 if task else 400,
                data=result.task.model_dump(),
            )
        except (
            ValidationError,
            TooManyRequestsError,
            NotFoundError,
            UnauthorizedError,
            UnknownError,
        ):
            pass

        return JsonResponse(status=403, data={})
