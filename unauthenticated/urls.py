from django.urls import path

from unauthenticated.views import LogoutView, SignInView

app_name = "unauthenticated"

urlpatterns = [
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", SignInView.as_view(), name="signin"),
]
