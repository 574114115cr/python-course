# pizzas/admin.py —— 注册两个模型
from django.contrib import admin

from .models import Pizza, Topping

admin.site.register(Pizza)
admin.site.register(Topping)
