from django.contrib import admin
# from django.contrib.auth.models import Permission

from core.models import User
from core.models import Order
from core.models import Tariff
from core.models.user import UserAdmin
from core.models.order import OrderAdmin
from core.models.tariff import TariffAdmin
from core.models.task import Task, TaskAdmin

admin.site.register(User, UserAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Tariff, TariffAdmin)
admin.site.register(Task, TaskAdmin)
# admin.site.register(Permission)
