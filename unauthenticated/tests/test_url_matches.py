from django.test import TestCase
from django.urls import NoReverseMatch, reverse

from unauthenticated.urls import urlpatterns


class TestUrlMatches(TestCase):
    def test_invalid_urls(self):
        msg = ""
        try:
            reverse("unauthenticated:some-404-url")
        except NoReverseMatch as e:
            msg = str(e)

        self.assertEqual(
            msg,
            "Reverse for 'some-404-url' not found. 'some-404-url' is not a valid view function or pattern name.",
        )

    def test_valid_urls(self):
        urls = {
            "logout": {"kwargs": {}, "sample": "/logout/"},
            "signin": {"kwargs": {}, "sample": "/"},
        }

        self.assertTrue(len(urls) == len(urlpatterns))

        for name, params in urls.items():
            if not params["kwargs"]:
                u = reverse(f"unauthenticated:{name}")
            else:
                u = reverse(f"unauthenticated:{name}", kwargs=params["kwargs"])

            self.assertEqual(params["sample"], u)
