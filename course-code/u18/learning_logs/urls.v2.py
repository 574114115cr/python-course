# learning_logs/urls.py —— 加上 about 路由
"""定义 learning_logs 的 URL 模式"""

from django.urls import path

from . import views

app_name = "learning_logs"

urlpatterns = [
    # 主页
    path("", views.index, name="index"),
    # 关于页面
    path("about/", views.about, name="about"),
    # 显示所有主题的页面
    path("topics/", views.topics, name="topics"),
    # 特定主题的详细页面
    path("topics/<int:topic_id>/", views.topic, name="topic"),
]
