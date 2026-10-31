# current_user_simulation.py —— request.user 到底是什么


class User:
    """已登录的用户对象。"""

    def __init__(self, username, user_id):
        self.username = username
        self.id = user_id
        self.is_authenticated = True


class AnonymousUser:
    """未登录用户的替身：Django 不给 None，而是给一个匿名对象。"""

    username = ""
    is_authenticated = False


# 已登录的请求：request.user 是真实的 User 对象
logged_in_request = {"user": User("eric", 1)}

# 未登录的请求：request.user 是 AnonymousUser
anonymous_request = {"user": AnonymousUser()}

for label, request in [("已登录", logged_in_request), ("未登录", anonymous_request)]:
    user = request["user"]
    print(f"{label}: is_authenticated={user.is_authenticated}, "
          f"username={user.username!r}")

print("\n=> 视图里写 request.user 永远拿得到对象：")
print("   登录了是 User，没登录是 AnonymousUser，不会 AttributeError")
print("   所以 filter(owner=request.user) 对未登录用户是安全的——")
print("   查不到任何数据，而不是崩溃")
