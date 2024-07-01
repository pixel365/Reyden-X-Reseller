from abc import ABC, abstractmethod
from typing import Self

from django.db import models

from pydantic import BaseModel


class _AbstractSyncModel(ABC):
    @staticmethod
    @abstractmethod
    def make_from_source(external_model: BaseModel, *args, **kwargs) -> Self | None: ...

    @abstractmethod
    def sync(self): ...

    @property
    @abstractmethod
    def details(self) -> BaseModel | None: ...


class AbstractSyncModel(models.Model):
    __metaclass__ = _AbstractSyncModel

    external_id = models.IntegerField(default=0, editable=False)
    platform = models.CharField(max_length=15, editable=False)

    class Meta:
        abstract = True
