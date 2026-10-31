# learning_logs/views.py —— 新增 about 视图
from django.shortcuts import render

from .models import Topic


def index(request):
    """学习笔记的主页。"""
    return render(request, "learning_logs/index.html")


def about(request):
    """关于页面：介绍这个项目是干什么的。"""
    return render(request, "learning_logs/about.html")


def topics(request):
    """显示所有主题。"""
    topics = Topic.objects.order_by("date_added")
    context = {"topics": topics}
    return render(request, "learning_logs/topics.html", context)


def topic(request, topic_id):
    """显示单个主题及其所有条目。"""
    topic = Topic.objects.get(id=topic_id)
    entries = topic.entry_set.order_by("-date_added")
    context = {"topic": topic, "entries": entries}
    return render(request, "learning_logs/topic.html", context)
