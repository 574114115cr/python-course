# template_inheritance_simulation.py —— {% block %} 和 {% extends %} 到底在干什么

BASE_HTML = """<!DOCTYPE html>
<html>
<head><title>学习笔记</title></head>
<body>
  <nav><a href="/">主页</a> | <a href="/topics/">主题</a></nav>
  <main>
    {% block content %}{% endblock content %}
  </main>
</body>
</html>"""


def render_page(base, block_content):
    """模拟模板继承：把子模板的内容填进 base 的 content 坑里。"""
    start_tag = "{% block content %}"
    end_tag = "{% endblock content %}"
    head = base[:base.index(start_tag)]
    tail = base[base.index(end_tag) + len(end_tag):]
    return head + block_content + tail


# 主页只写自己关心的部分
index_body = "<h1>学习笔记</h1><p>欢迎回来！</p>"

# 主题页也只写自己关心的部分
topics_body = "<h1>所有主题</h1><ul><li>Python</li><li>Django</li></ul>"

index_page = render_page(BASE_HTML, index_body)
topics_page = render_page(BASE_HTML, topics_body)

print("=== 主页 ===")
print(index_page)
print("\n=== 主题页 ===")
print(topics_page)

# 两个页面共享完全一致的导航栏，因为它来自同一份 base.html
nav_index = index_page.split("<main>")[0]
nav_topics = topics_page.split("<main>")[0]
print("\n两个页面的导航栏完全一致：", nav_index == nav_topics)
print("=> 想改导航？只改 base.html 一处，所有页面自动生效")
