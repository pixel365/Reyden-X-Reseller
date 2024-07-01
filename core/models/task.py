from datetime import datetime, timezone
import json
from typing import Self
from django.db import models
from django.contrib.admin import ModelAdmin

from django.http import HttpRequest
from pyreydenx.model.task import TaskStatusChoices, ActionResult


class Task(models.Model):
    _details = None
    _details_cache = False

    user = models.ForeignKey(
        to="core.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default=None,
        editable=False,
    )
    external_id = models.CharField(max_length=256, unique=True, editable=False)
    status = models.CharField(default="pending", max_length=50, editable=False)
    order_id = models.IntegerField(default=0, editable=False)
    action = models.CharField(max_length=100, editable=False)
    source = models.TextField(blank=False, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ["-pk"]
        indexes = [
            models.Index(fields=("status",)),
            models.Index(fields=("external_id",)),
            models.Index(fields=("order_id",)),
        ]

    def __str__(self) -> str:
        return f"{__class__.__name__} #{self.pk}"

    def __repr__(self) -> str:
        return f"<{__class__.__name__} #{self.pk}: {self.action}>"

    @property
    def details(self) -> ActionResult:
        if self._details_cache:
            return self._details

        if len(self.source):
            self._details_cache = True
            self._details = ActionResult(**json.loads(self.source))

        return self._details

    @property
    def check_period_expired(self) -> bool:
        if self.status in (
            TaskStatusChoices.COMPLETED,
            TaskStatusChoices.ERROR,
        ):
            return True

        if self.details:
            return datetime.now(tz=timezone.utc) >= self.details.task.expires_at

        return True

    def complete(self, order_id: int) -> bool:
        if self.status in (
            TaskStatusChoices.ACTION_REQUIRED,
            TaskStatusChoices.ERROR,
            TaskStatusChoices.COMPLETED,
        ):
            return False

        self.status = TaskStatusChoices.COMPLETED
        self.order_id = order_id
        self.updated_at = datetime.now(tz=timezone.utc)
        self.save(update_fields=["status", "order_id", "updated_at"])
        return True

    def error(self, status: TaskStatusChoices):
        if self.status in (
            TaskStatusChoices.ACTION_REQUIRED,
            TaskStatusChoices.ERROR,
            TaskStatusChoices.COMPLETED,
        ):
            return False

        self.status = status
        self.updated_at = datetime.now(tz=timezone.utc)
        self.save(update_fields=["status", "updated_at"])

    @staticmethod
    def make_from_source(request: HttpRequest, source: ActionResult) -> Self | None:
        try:
            Task.objects.get(external_id=source.task.id)
            return None
        except Task.DoesNotExist:
            pass

        model = Task()
        model.user = request.user
        model.external_id = source.task.id
        model.status = TaskStatusChoices.PENDING
        if source.order_id:
            model.order_id = source.order_id
        model.action = source.action
        model.source = source.model_dump_json()
        model.save()

        if model.pk:
            return model
        return None


class TaskAdmin(ModelAdmin):
    list_display = (
        "pk",
        "created_at",
        "user",
        "external_id",
        "status",
        "order_id",
        "action",
    )
    list_filter = (
        "created_at",
        "status",
        "action",
    )
    exclude = ()
