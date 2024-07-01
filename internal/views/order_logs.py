from typing import Any

from django.http import Http404
from django.urls import reverse_lazy
from core.mixins import IsAdminMixin

from django.views.generic import ListView
from django.utils.translation import gettext_lazy as _

from core.models.order import Order
from core.models.task import Task
from reseller.settings import EL_PAGINATION_PER_PAGE


class OrderLogsView(IsAdminMixin, ListView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.template_name = "internal/pages/order_logs.html"
        self.paginate_by = EL_PAGINATION_PER_PAGE
        self.model = Task
        self.order = None

    def get_queryset(self):
        try:
            self.order = Order.objects.get(pk=self.kwargs["pk"])
        except Order.DoesNotExist:
            raise Http404

        self.queryset = Task.objects.filter(order_id=self.order.external_id)
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            self.queryset = self.queryset.order_by(*ordering)

        return self.queryset

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = _("Order Logs")
        context["pages"] = range(1, len(self.queryset) + 1)
        context["breadcrumbs"] = [
            {
                "name": self.order.platform.capitalize() + " " + _("Orders"),
                "url": reverse_lazy(f"internal:{self.order.platform}"),
            },
            {
                "name": self.order,
                "url": reverse_lazy("internal:order", kwargs={"pk": self.kwargs["pk"]}),
            },
            {"name": _("Logs"), "url": None},
        ]

        return context
