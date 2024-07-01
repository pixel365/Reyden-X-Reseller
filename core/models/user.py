from typing import List, Optional, Self
from django.contrib.auth.models import AbstractUser
from django.contrib.admin import ModelAdmin
from django.db import models
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password

from core.helpers import Perms


class User(AbstractUser):
    password = models.CharField(_("password"), max_length=128, editable=False)

    class Meta:
        permissions = [
            (Perms.CAN_VIEW_PRICES.value, "Can see the cost in the tariffs"),
            (Perms.CAN_VIEW_BALANCE.value, "Can see the balance on the main balance"),
            (Perms.CAN_VIEW_TWITCH_ORDERS.value, "Can see Twitch orders"),
            (Perms.CAN_VIEW_YOUTUBE_ORDERS.value, "Can see YouTube orders"),
            (Perms.CAN_CREATE_TWITCH_ORDERS.value, "Can create Twitch orders"),
            (Perms.CAN_CREATE_YOUTUBE_ORDERS.value, "Can create YouTube orders"),
        ]

    def __str__(self) -> str:
        return self.username

    def __repr__(self) -> str:
        return f"<{__class__.__name__} #{self.pk}: {self.username}>"

    def clean_fields(self, *args, **kwargs) -> None:
        return super().clean_fields(*args, **kwargs)

    @staticmethod
    def make(username: str, password: str) -> Self | List:
        try:
            User.objects.get(username=username)
            return [_("This username is taken")]
        except User.DoesNotExist:
            pass

        try:
            validate_password(password)
            model = User()
            model.username = username
            model.set_password(password)
            model.clean_fields()
            model.save()
            return model
        except ValidationError as e:
            errs = []
            if e.error_list:
                for err in e.error_list:
                    errs.extend(err.messages)
            return errs


class UserAdmin(ModelAdmin):
    list_display = (
        "pk",
        "username",
        "is_active",
        "date_joined",
    )
    exclude = ()

    def has_delete_permission(
        self, request: HttpRequest, obj: Optional[User] = None
    ) -> bool:
        if obj:
            return not obj.is_superuser and request.user.is_superuser
        return request.user.is_superuser
