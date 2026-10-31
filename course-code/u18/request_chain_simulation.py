# request_chain_simulation.py —— 60 行复现 Django 处理一次请求的全过程
# 对应关系：urlpatterns = urls.py，视图函数 = views.py，render() = 模板渲染

# ===== 1）路由表：相当于 learning_logs/urls.py 里的 urlpatterns =====
urlpatterns = []


def route(path):
    """注册路由。@route('topics/') 等价于 path('topics/', views.topics)。"""
    def decorator(view_func):
        urlpatterns.append((path, view_func))
        return view_func
    return decorator


# ===== 2）模板：相当于 templates/learning_logs/*.html =====
TEMPLATES = {
    "index.html": "<h1>学习笔记</h1><p>已记录 {count} 个主题。</p>",
    "topics.html": "<h1>主题</h1><ul>{items}</ul>",
}


# ===== 3）render()：把 context 字典的数据填进模板 =====
def render(template_name, context):
    html = TEMPLATES[template_name]
    for key, value in context.items():
        html = html.replace("{" + key + "}", str(value))
    return html


# ===== 4）视图：相当于 views.py 里的函数 =====
@route("")
def index(request):
    """主页视图：不查数据库，直接渲染模板。"""
    return render("index.html", {"count": 3})


@route("topics/")
def topics(request):
    """主题列表视图：先查数据，装进 context，再渲染。"""
    topic_list = ["Python", "Django", "Git"]
    items = "".join(f"<li>{t}</li>" for t in topic_list)
    return render("topics.html", {"items": items})


# ===== 5）Django 的「接线员」：按 URL 找到对应视图 =====
def handle_request(url):
    print(f"浏览器请求：GET /{url}")
    for path, view_func in urlpatterns:
        if url == path:
            print(f"  urls.py 匹配 {path!r} -> 调用视图 {view_func.__name__}()")
            html = view_func({"path": url})      # request 在这里只是个字典
            print(f"  render() 渲染完成，返回 {len(html)} 字符的 HTML")
            return html
    print("  没有匹配的 URL 模式 -> 404 Not Found")
    return None


# ===== 测试三次访问 =====
print("--- 访问主页 ---")
print(handle_request(""))
print("\n--- 访问主题页 ---")
print(handle_request("topics/"))
print("\n--- 访问不存在的页面 ---")
print(handle_request("不存在/"))
