from django.http import HttpResponseRedirect
from django.test import TestCase
from django.urls import reverse
from django.template.response import TemplateResponse
from django.contrib.messages.storage import (
    base,
    fallback
)

from core.helpers import Platform
from core.models.user import User


class TestAccess(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testing", password="123456")
        self.user.save()

    def tearDown(self):
        self.user.delete()

    def test_success(self):
        response = self.client.post(reverse("unauthenticated:signin"), data={
            "username": "testing",
            "password": "123456"
        })

        self.assertEqual(response.status_code, 302)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.url, reverse(f"internal:{Platform.TWITCH}"))

    def test_empty_creds(self):
        response = self.client.post(reverse("unauthenticated:signin"), data={
            "username": "",
            "password": ""
        })

        self.assertEqual(response.status_code, 401)
        self.assertIsInstance(response, TemplateResponse)


        messages = response.__dict__.get("context").get("messages")
        self.assertIsInstance(messages, fallback.FallbackStorage)
        self.assertTrue("_loaded_data" in messages.__dict__)

        messages = messages.__dict__["_loaded_data"]

        self.assertIsInstance(messages[0], base.Message)
        self.assertIsInstance(messages[1], base.Message)

        self.assertTrue(
            all((messages[0].level == 40, messages[0].message == "Username is required."))
        )
        self.assertTrue(
            all((messages[1].level == 40, messages[1].message == "Password is required."))
        )

    def test_invalid_creds(self):
        response = self.client.post(reverse("unauthenticated:signin"), data={
            "username": "fake",
            "password": "fake"
        })

        self.assertEqual(response.status_code, 401)
        self.assertIsInstance(response, TemplateResponse)


        messages = response.__dict__.get("context").get("messages")
        self.assertIsInstance(messages, fallback.FallbackStorage)
        self.assertTrue("_loaded_data" in messages.__dict__)

        messages = messages.__dict__["_loaded_data"]

        self.assertIsInstance(messages[0], base.Message)

        self.assertTrue(
            all((messages[0].level == 40, messages[0].message == "Failed to login. Check your login and password."))
        )
