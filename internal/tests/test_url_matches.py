from django.test import TestCase
from django.urls import reverse, NoReverseMatch

from core.helpers import Platform
from internal.urls import urlpatterns


class TestUrlMatches(TestCase):
    def test_invalid_urls(self):
        msg = ""
        try:
            reverse("internal:some-404-url")
        except NoReverseMatch as e:
            msg = str(e)

        self.assertEqual(msg, "Reverse for 'some-404-url' not found. 'some-404-url' is not a valid view function or pattern name.",)

    def test_valid_urls(self):
        urls = {
            "add-user":{
                "kwargs": {},
                "sample": "/internal/add-user/"
            },
            "order-logs": {
                "kwargs": {
                    "pk": 1
                },
                "sample": "/internal/1/logs/"
            },
            "order": {
                "kwargs": {
                    "pk": 1
                },
                "sample": "/internal/1/"
            },
            Platform.TWITCH.value: {
                "kwargs": {},
                "sample": f"/internal/{Platform.TWITCH}/"
            },
            Platform.YOUTUBE.value: {
                "kwargs": {},
                "sample": f"/internal/{Platform.YOUTUBE}/"
            },
            f"new-{Platform.TWITCH}": {
                "kwargs": {},
                "sample": f"/internal/{Platform.TWITCH}/new/"
            },
            f"new-{Platform.YOUTUBE}": {
                "kwargs": {},
                "sample": f"/internal/{Platform.YOUTUBE}/new/"
            },
        }

        self.assertTrue(len(urls) == len(urlpatterns))

        for name, params in urls.items():
            if not params["kwargs"]:
                u = reverse(f"internal:{name}")
            else:
                u = reverse(f"internal:{name}", kwargs=params["kwargs"])

            self.assertEqual(params["sample"], u)
