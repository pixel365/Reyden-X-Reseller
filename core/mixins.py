from django.contrib.auth.mixins import LoginRequiredMixin as LRM
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.urls import reverse_lazy


class LoginRequiredMixin(LRM):
    login_url = reverse_lazy("unauthenticated:signin")


class IsAdminMixin(LoginRequiredMixin):
    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_superuser:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
