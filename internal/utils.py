from django.http import HttpRequest
from django.db.models import QuerySet, Q

from core.helpers import OrderStatus, Platform, Perms
from core.models.order import Order


def make_orders_queryset(
    request: HttpRequest, platform: Platform, perms: tuple[Perms]
) -> QuerySet:
    filter = {}
    user = request.user

    if not user.has_perms(perms):
        filter["user"] = user

    s = request.GET.get("s", None)
    if s in {x for _, x in OrderStatus.__members__.items()}:
        filter["status"] = s

    if q := request.GET.get("q", "").strip(" "):
        try:
            oid = int(q)
            if oid > 0:
                f = Q(external_id=oid)
            else:
                f = Q(pk__gt=0)
        except ValueError:
            f = Q(channel_search_content__icontains=q.lower())

        return Order.objects.filter(f, platform=platform, **filter)
    else:
        return Order.objects.filter(platform=platform, **filter)
