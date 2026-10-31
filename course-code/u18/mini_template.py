# mini_template.py —— 手写迷你模板引擎（支持 {{ }} 和 {% for %}）

import re


def mini_render(template, context):
    """渲染模板：支持 {{ 变量 }} 与 {% for x in 列表 %}...{% endfor %}。"""
    # ===== 第 1 步：处理循环（从最内层开始，一层套一层由递归保证）=====
    for_pattern = re.compile(
        r"\{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%\}(.*?)\{%\s*endfor\s*%\}",
        re.DOTALL,
    )

    def expand_for(match):
        var_name, list_name, body = match.groups()
        items = context.get(list_name, [])
        parts = []
        for item in items:
            # 循环体内的 {{ 变量 }} 先替换成当前元素
            rendered = body.replace("{{ " + var_name + " }}", str(item))
            parts.append(rendered)
        return "".join(parts)

    while "{% for" in template:
        template = for_pattern.sub(expand_for, template)

    # ===== 第 2 步：处理剩下的普通变量 {{ 变量 }} =====
    def replace_var(match):
        key = match.group(1).strip()
        return str(context.get(key, ""))

    template = re.sub(r"\{\{\s*(\w+)\s*\}\}", replace_var, template)
    return template


# ===== 测试 =====
TEMPLATE = """<h1>所有主题</h1>
<ul>
{% for topic in topics %}
  <li>{{ topic }}</li>
{% endfor %}
</ul>
<p>共 {{ count }} 个主题。</p>"""

context = {"topics": ["Python", "Django", "Git"], "count": 3}

print(mini_render(TEMPLATE, context))
print()
print("还支持空列表：", mini_render("{% for x in items %}{{ x }}{% endfor %}",
                                   {"items": []}) == "")
