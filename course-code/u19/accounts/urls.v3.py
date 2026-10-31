# accounts/urls.py —— 登录/注销：Django 自带视图，只需包含默认 URL
"""为应用程序 accounts 定义 URL 模式"""

from django.urls import path, include

app_name = "accounts"

urlpatterns = [
    # 包含默认的身份验证 URL
    path("", include("django.contrib.auth.urls")),
]
