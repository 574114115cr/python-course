# ll_project/urls.py —— 挂上 accounts 的 URL
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", include("learning_logs.urls")),
]
