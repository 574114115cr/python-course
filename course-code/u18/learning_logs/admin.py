# learning_logs/admin.py —— 向管理网站注册模型（不注册，后台就看不到）
from django.contrib import admin

from .models import Topic, Entry

admin.site.register(Topic)
admin.site.register(Entry)
