from datetime import datetime, timezone
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.db.models import QuerySet
from django.contrib.auth.models import Permission, Group, AnonymousUser
from django.contrib.contenttypes.models import ContentType

from core.helpers import Perms, Platform
from core.models.order import Order
from core.models.tariff import Tariff
from core.models.tariff_category import TariffCategory
from core.models.user import User
from internal.views.youtube import YouTubeView
from reseller.settings import EL_PAGINATION_PER_PAGE

class YouTubeViewTest(TestCase):
    def setUp(self):
        self.order = None
        self.group = Group.objects.create(name="test group")
        self.group.save()
        self.group.permissions.add(
            Permission.objects.get(
                content_type=ContentType.objects.get(app_label="core", model="user"), 
                codename=Perms.CAN_VIEW_YOUTUBE_ORDERS
            )
        )
        self.group.save()

        self.category = TariffCategory.objects.create(
            name="some name",
            description="some description",
            external_id=1,
            synchronized_at=datetime.now(tz=timezone.utc),
        )
        self.category.save()

        self.tariff = Tariff.objects.create(
            name="some name",
            description="some description",
            value=0.1,
            category=self.category,
            external_value=0.1,
            synchronized_at=datetime.now(tz=timezone.utc),
        )
        self.tariff.save()

        self.user = User.objects.create_user(username="testing", password="123456")
        self.user.save()
        self.user.groups.add(self.group)
        self.user.save()

        self.order = Order.objects.create(
            user=self.user,
            tariff=self.tariff,
            platform=Platform.YOUTUBE,
            channel_search_content="testing",
            synchronized_at=datetime.now(tz=timezone.utc),
        )

        self.request = RequestFactory().get(reverse(f"internal:{Platform.YOUTUBE}"))
        self.request.user = self.user

    def tearDown(self) -> None:
        self.group.delete()
        self.category.delete()
        self.tariff.delete()
        self.user.delete()

        if isinstance(self.order, Order) and self.order.pk:
            self.order.delete()

    def test_init(self):
        view = YouTubeView()
        view.setup(self.request)

        self.assertIs(view.model, Order)
        self.assertEqual(view.template_name, "internal/pages/list_of_orders.html")
        self.assertEqual(view.paginate_by, EL_PAGINATION_PER_PAGE)

    def test_queryset(self):
        view = YouTubeView()
        view.setup(self.request)

        self.assertIsInstance(view.get_queryset(), QuerySet)
        self.assertEqual(len(view.get_queryset()), 1)
        self.assertEqual(view.get_queryset()[0].pk, self.order.pk)

        self.order.delete()
        self.assertEqual(len(view.get_queryset()), 0)


    def test_ok(self):
        self.request.user = self.user
        response = YouTubeView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_anonymous(self):
        self.request.user = AnonymousUser()
        response = YouTubeView.as_view()(self.request)
        self.assertEqual(response.status_code, 403)

    def test_no_permissions(self):
        self.user.groups.clear()
        self.user.save()
        
        self.request.user = User.objects.get(pk=1)
        response = YouTubeView.as_view()(self.request)
        self.assertEqual(response.status_code, 403)

