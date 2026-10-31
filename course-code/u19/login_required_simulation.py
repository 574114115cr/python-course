# login_required_simulation.py —— 装饰器是怎么当上门禁的


def login_required(view_func):
    """模拟 Django 的 @login_required：没登录就不放行。"""

    def wrapper(request, *args, **kwargs):
        user = request.get("user")
        if user is None or not user.get("is_authenticated"):
            print("  门禁：未登录 -> 重定向到登录页（settings.LOGIN_URL）")
            return "重定向到 /accounts/login/"
        return view_func(request, *args, **kwargs)

    return wrapper


@login_required
def topics(request):
    """受保护的主题列表视图。"""
    return "主题列表页面（只含当前用户的主题）"


# 场景一：已登录用户
print("已登录用户访问：")
print(" ", topics({"user": {"is_authenticated": True, "username": "eric"}}))

# 场景二：未登录用户
print("\n未登录用户访问：")
print(" ", topics({"user": {"is_authenticated": False}}))

print("\n=> 装饰器不改变视图本身的代码，只是在门口加了一道检查：")
print("   忘写 @login_required，等于门禁没上岗，谁都能推门进去")
