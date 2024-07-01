import os
from django.http import HttpRequest

from core.models.balance import Balance


def extend(request: HttpRequest):
    return {
        "currency": os.getenv("CURRENCY", "dollar"),
        "balance": Balance.get_balance(),
    }
