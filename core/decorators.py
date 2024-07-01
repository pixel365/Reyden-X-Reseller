from functools import wraps, partial

from django.http import (
    HttpResponseForbidden,
    HttpRequest,
    HttpResponseBadRequest,
)

from core.helpers import Perms


def check_perms(f: partial, perms: tuple[Perms]):
    @wraps(f)
    def wrap(request: HttpRequest, *args, **kwargs):
        if len(perms) < 1:
            raise HttpResponseBadRequest

        u = request.user
        if not any(u.has_perm(f"core.{perm}") for perm in perms):
            return HttpResponseForbidden

        return f(request, *args, **kwargs)

    return wrap
