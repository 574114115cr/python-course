# accounts/views.py —— 注册视图
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm


def register(request):
    """注册新用户。"""
    if request.method != "POST":
        form = UserCreationForm()
    else:
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            new_user = form.save()
            # 让用户自动登录，再重定向到主页
            login(request, new_user)
            return redirect("learning_logs:index")

    context = {"form": form}
    return render(request, "registration/register.html", context)
