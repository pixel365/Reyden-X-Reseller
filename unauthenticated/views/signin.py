from functools import wraps
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.template.response import TemplateResponse
from django.contrib import messages, auth
from django.utils.translation import gettext as _

from core.helpers import Platform


def _redirect_if_authenticated(f):
    @wraps(f)
    def wrap(request: HttpRequest, *args, **kwargs):
        if hasattr(request, "user"):
            if request.user.is_authenticated:
                return HttpResponseRedirect(reverse("internal:index"))
        return f(request, *args, **kwargs)

    return wrap


@method_decorator(_redirect_if_authenticated, name="dispatch")
class SignInView(TemplateView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template_name = "unauthenticated/pages/signin.html"

    def get(self, request: HttpRequest, *args, **kwargs):
        return TemplateResponse(
            request=request, template=self.template_name, context={}
        )

    def post(self, request: HttpRequest, *args, **kwargs):
        errors = messages.get_messages(request)
        if len(errors) < 1:
            username = request.POST.get("username")
            password = request.POST.get("password")
            if username and password:
                if user := auth.authenticate(
                    request, username=username, password=password
                ):
                    auth.login(request=request, user=user)
                    return HttpResponseRedirect(reverse(f"internal:{Platform.TWITCH}"))
                else:
                    messages.error(
                        request=request,
                        message=_("Failed to login. Check your login and password."),
                    )
            else:
                if not username:
                    messages.error(request=request, message=_("Username is required."))
                if not password:
                    messages.error(request=request, message=_("Password is required."))

        return TemplateResponse(
            request=request, status=401, template=self.template_name, context={}
        )
