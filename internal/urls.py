from django.urls import path

from core.helpers import Platform
from internal.views import TwitchView, YouTubeView, OrderDetailsView
from internal.views.add_user import AddUserView
from internal.views.new_order.twitch import NewTwitch
from internal.views.new_order.youtube import NewYouTube
from internal.views.order_logs import OrderLogsView

app_name = "internal"

urlpatterns = [
    path("add-user/", AddUserView.as_view(), name="add-user"),
    path("<int:pk>/logs/", OrderLogsView.as_view(), name="order-logs"),
    path("<int:pk>/", OrderDetailsView.as_view(), name="order"),
    path(f"{Platform.TWITCH}/new/", NewTwitch.as_view(), name=f"new-{Platform.TWITCH}"),
    path(
        f"{Platform.YOUTUBE}/new/",
        NewYouTube.as_view(),
        name=f"new-{Platform.YOUTUBE}",
    ),
    path(f"{Platform.TWITCH}/", TwitchView.as_view(), name=Platform.TWITCH),
    path(f"{Platform.YOUTUBE}/", YouTubeView.as_view(), name=Platform.YOUTUBE),
]
