from typing import Any

from django.http import HttpRequest, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from core.mixins import IsAdminMixin
from core.models.user import User


class AddUserView(IsAdminMixin, TemplateView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.template_name = "internal/pages/add_user.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> TemplateResponse:
        context = {
            "title": _("Add User"),
        }
        return TemplateResponse(
            request=request, template=self.template_name, context=context
        )

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any):
        errors = messages.get_messages(request)
        if len(errors) < 1:
            username = request.POST.get("username")
            password = request.POST.get("password")
            if username and password:
                result = User.make(username, password)
                if isinstance(result, User):
                    return HttpResponseRedirect(reverse("internal:add-user"))
                else:
                    for m in result:
                        messages.error(request=request, message=m)
            else:
                if not username:
                    messages.error(request=request, message=_("Username is required."))
                if not password:
                    messages.error(request=request, message=_("Password is required."))

        return TemplateResponse(
            request=request, status=401, template=self.template_name, context={}
        )
