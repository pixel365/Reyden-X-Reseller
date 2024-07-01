from typing import Any

from functools import partial

from django.http.response import HttpResponse as HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from core.decorators import check_perms
from core.helpers import OrderStatus, Perms, Platform
from core.mixins import LoginRequiredMixin
from core.models.order import Order
from internal.utils import make_orders_queryset
from reseller.settings import EL_PAGINATION_PER_PAGE

_check_perms = partial(
    check_perms,
    perms=(
        Perms.CAN_VIEW_YOUTUBE_ORDERS,
        Perms.CAN_CREATE_YOUTUBE_ORDERS,
    ),
)


@method_decorator(_check_perms, name="dispatch")
class YouTubeView(LoginRequiredMixin, ListView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.template_name = "internal/pages/list_of_orders.html"
        self.paginate_by = EL_PAGINATION_PER_PAGE
        self.model = Order

    def get_queryset(self):
        self.queryset = make_orders_queryset(
            request=self.request, platform=Platform.YOUTUBE
        )
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            self.queryset = self.queryset.order_by(*ordering)

        return self.queryset

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = _("YouTube Orders")
        context["pages"] = range(1, len(self.queryset) + 1)
        context["show_filter"] = True
        context["statuses"] = {x for _, x in OrderStatus.__members__.items()}

        if self.request.user.has_perm(Perms.CAN_CREATE_YOUTUBE_ORDERS):
            context["create_order_url"] = reverse_lazy(
                f"internal:new-{Platform.YOUTUBE}"
            )

        return context
