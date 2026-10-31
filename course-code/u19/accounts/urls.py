# accounts/urls.py —— 默认 URL 白拿 login / logout，register 用自己的视图
from django.urls import path, include

from . import views

app_name = "accounts"

urlpatterns = [
    # 包含默认的身份验证 URL
    path("", include("django.contrib.auth.urls")),
    # 注册页面（自己写）
    path("register/", views.register, name="register"),
]
