# ll_project/urls.py —— 项目的总路由：把 learning_logs 开头的请求转给 app
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("learning_logs.urls")),
]
