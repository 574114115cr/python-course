# accounts/urls.py —— 登录/注销用自带视图，注册用自己的
"""为应用程序 accounts 定义 URL 模式"""

from django.urls import path, include

from . import views

app_name = "accounts"

urlpatterns = [
    # 包含默认的身份验证 URL
    path("", include("django.contrib.auth.urls")),
    # 注册页面
    path("register/", views.register, name="register"),
]
