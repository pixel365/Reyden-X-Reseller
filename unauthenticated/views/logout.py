from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import logout
from django.views.generic import TemplateView


class LogoutView(TemplateView):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect:
        if hasattr(request, "user"):
            if request.user.is_authenticated:
                logout(request)
        return HttpResponseRedirect(reverse("unauthenticated:signin"))
