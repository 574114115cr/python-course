# 单元 18：Django 入门

> 对应教材第 18 章「Django 入门」
> 阶段 2 · 项目 3：学习笔记（Learning Log）
> 本单元目标：**从零搭起一个能跑的 Django 项目——建虚拟环境、建项目、写模型、配好管理网站，并用「URL → 视图 → 模板」链路渲染出第一个网页。**

---

## 一、学习目标

完成本单元后，你应该能够：

1. 独立完成「建虚拟环境 → 激活 → 安装 Django → startproject → startapp → migrate → runserver」全流程，并说出**虚拟环境到底解决什么问题**，以及 Windows / macOS / Linux 三条激活命令。
2. 画出 `learning_log/`、`ll_project/`、`learning_logs/` 三者的目录关系，解释**项目（project）**与**应用程序（app）**的分工，以及模型、视图、模板（MVT）各自负责什么。
3. 编写模型并走完「改 `models.py` → `makemigrations` → `migrate`」三步曲，解释「迁移文件是数据库的施工图纸」，并用管理网站和 Django shell 查看、添加数据。
4. 完整走通一次请求的旅程：浏览器输入 URL → `urls.py` 路由 → `views.py` 处理 → `render()` 渲染模板 → 返回响应，并能说清每一步改了哪个文件、会影响什么。
5. 用模板继承把公共部分收进 `base.html`，并用 `{{ }}`、`{% for %}`、`{% url %}` 写出显示数据的页面。

---

## 二、核心知识点讲解

### 2.1 虚拟环境：给每个项目一间独立的「工具间」★

这是整个阶段 2 的第一个大坑，先说清楚：**为什么 Django 之前必须先建虚拟环境**。

生活化类比：不同项目需要的工具不一样——项目 A 要 Django 5.0，项目 B 可能还赖在 Django 4.2 上不肯升级。如果所有包都塞进系统里同一个 Python，就像把木工的电锯和电工的万用表扔进同一间屋子：互相打架，谁也别想干活。**虚拟环境就是给每个项目单独隔出一间工具间**，工具只在本房间有效，出了门就看不见。

| 系统 | 创建（只需一次） | 激活（每开一个新终端都要做） | 退出 |
|---|---|---|---|
| Windows（命令行） | `python -m venv ll_env` | `ll_env\Scripts\activate` | `deactivate` |
| Windows（PowerShell） | 同上 | `ll_env\Scripts\Activate`（A 大写） | `deactivate` |
| macOS / Linux | `python -m venv ll_env` | `source ll_env/bin/activate` | `deactivate` |

激活成功的标志：**命令行提示符前面出现了 `(ll_env)`**。没出现，就说明工具间的门根本没开，后面所有命令都会出怪问题。

```bash
# 18.1.2 ~ 18.1.4：建目录、建虚拟环境、装 Django（教材原命令）
mkdir learning_log
cd learning_log
python -m venv ll_env
source ll_env/bin/activate        # Windows 用 ll_env\Scripts\activate
(ll_env)learning_log$ pip install --upgrade pip
(ll_env)learning_log$ pip install django
```

三个必须记住的细节：

- **`ll_env` 是两个小写的 L 加 `env`**，不是数字 1。教材特意提醒过这一点。
- **`pip install` 前一定看一眼有没有 `(ll_env)`**。没有它，Django 会被装到全局 Python 里，当下也能跑，但换台机器、换个项目就是一堆兼容性噩梦。
- 关闭终端 = 虚拟环境自动失效，下次开工要重新激活。这是新手最常犯的错，没有之一：昨天明明跑得好好的，今天一开终端全报 `ModuleNotFoundError: No module named 'django'`——99% 是忘了激活。

本讲义基于 Django 5.x（执行 `pip install django` 装到的最新稳定版）。教材写作时用的是 4.1，但本单元涉及的所有 API 在两个版本中完全一致。

### 2.2 Django 的三个层次：项目、应用程序、MVT ★

新手在 Django 里迷路，90% 是因为分不清**项目**和**应用程序**。先看目录，再看类比：

```text
learning_log/                  ← 你亲手建的工作目录（所有命令都在这里执行）
├── ll_env/                    ← 虚拟环境「工具间」，Django 住在里面
├── ll_project/                ← 项目（project）：配置的家，全项目只有一份
│   ├── settings.py            ←   项目总控室：装了什么 app、数据库在哪
│   ├── urls.py                ←   项目总前台：把请求分发给各个 app
│   └── wsgi.py                ←   部署时用的服务器接口（本单元用不到）
├── learning_logs/             ← 应用程序（app）：真正干活的地方
│   ├── models.py              ←   数据长什么样（M：模型）
│   ├── views.py               ←   拿到数据怎么处理（V：视图）
│   ├── admin.py               ←   管理网站的登记处
│   ├── migrations/            ←   数据库的施工图纸存档
│   └── templates/             ←   页面长什么样（T），18.3 节才创建
│       └── learning_logs/     ←     再套一层 app 名，防止模板名撞车
├── db.sqlite3                 ← 数据库本体：一个文件就是一整个数据库
└── manage.py                  ← Django 的遥控器：所有管理命令都靠它发出
```

模板为什么要套两层（`learning_logs/templates/learning_logs/`）？教材的解释是：这好像有点多余，但建立了 Django 能够明确解读的结构——项目变大、app 变多之后，不同 app 里有同名模板（比如都叫 `index.html`）也不会搞混。视图里写 `render(request, "learning_logs/index.html")` 这个路径时，前面的 `learning_logs/` 就是在指这层目录。

- **项目（project）= 餐厅的营业执照和规章制度**。全项目一份，规定「本店用什么灶、账记在哪」。
- **应用程序（app）= 厨房、收银台、库房**。可以有很多个，各干各的活；它们协同工作，让项目成为一个整体。本项目先只有一个 `learning_logs`，第 19 章会加第二个 `accounts`。

Django 信奉 **MVT 三件套**，和你在单元 8 学过的「类」无缝衔接：

| 字母 | 名字 | 文件 | 职责 | 类比 |
|---|---|---|---|---|
| M | Model 模型 | `models.py` | 数据长什么样、怎么存 | 仓库的库存账 |
| V | View 视图 | `views.py` | 拿到数据怎么加工 | 厨师 |
| T | Template 模板 | `templates/` 下的 `.html` | 数据以什么长相呈现 | 摆盘 |

**`settings.py` 里的 `INSTALLED_APPS`**：每新建一个 app，都要来这里「注册学籍」——不登记，Django 就不知道它的存在：`migrate` 不会给它的模型建表，管理网站也看不到它。

```python
# ll_project/settings.py（片段）——把 learning_logs 加进 INSTALLED_APPS
INSTALLED_APPS = [
    # 我的应用程序
    'learning_logs',

    # Django 默认添加的应用程序
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
```

为什么要分组、还要把自己的 app 放在默认应用前面？教材的说法是：项目变大、app 变多之后，分组让你一眼看清谁是谁；自己写的 app 放前面，才能覆盖默认 app 的行为。

### 2.3 模型 → 迁移 → 数据库：改数据的「三步曲」★

模型就是单元 8 学过的类，只不过它继承自 Django 的 `models.Model`。改完模型，数据库不会自动跟着变——必须走三步曲：

| 步骤 | 命令 | 在干什么 | 类比 |
|---|---|---|---|
| ① 改模型 | 编辑 `models.py` | 告诉 Django 你想要什么数据结构 | 建筑师改图纸 |
| ② 生成迁移 | `python manage.py makemigrations learning_logs` | 把改动翻译成施工图纸，存进 `migrations/0001_initial.py` | 把图纸晒成施工队能看懂的版本 |
| ③ 应用迁移 | `python manage.py migrate` | 照图纸真正修改数据库 | 施工队照图施工 |

**迁移文件就是数据库的施工图纸**——它记录「上次数据库长这样，这次要加一张表 / 加一列」。有了它，数据库的任何改动都有据可查、可以回放，换台电脑也能从零施工出一模一样的数据库。

最常见的翻车：只做了 ①②漏了 ③，或者 ① 做完就跑去刷新网页，然后看到 `OperationalError: no such table`——图纸画了没人施工，数据库还是空地一块。

**管理网站 `/admin/`** 是 Django 白送的后台：先建一个超级用户（相当于总经理，手握所有房间的钥匙）。

```bash
python manage.py createsuperuser   # 按提示输入用户名、邮箱（可空）、密码两次
python manage.py runserver         # 然后浏览器访问 http://127.0.0.1:8000/admin/
```

**Django shell**（`python manage.py shell`）是调试神器：它启动一个带项目环境的 Python 解释器，让你**不进网页直接查数据库**。类比：不用推门进房，直接趴窗户上看里面。写查询代码时，先在 shell 里试通，能跑对再抄进 `views.py`——在简单的 shell 里排错，比在生成网页的一堆文件里排错容易得多。退出按 `Ctrl+D`（Windows 先按 `Ctrl+Z` 再回车）。

### 2.4 一对多：Topic 和 Entry 的外键 ★

学习笔记的数据长这样：一个**主题**（比如「Python」）下面挂着很多**条目**（今天学的一点、明天学的一点）。这叫**多对一**关系——多个条目关联到同一个主题。Django 用**外键**表达它，在 `Entry` 模型里写一行 `topic = models.ForeignKey(Topic, on_delete=models.CASCADE)`（示例 4 有完整代码）。

翻译成人话：每条 Entry 身上都有一列，记住「我属于哪个 Topic」。

`on_delete=models.CASCADE` 回答的是一个尖锐问题：**主题被删了，挂在它下面的条目怎么办？** `CASCADE`（级联删除）的答案是——一起删。类比：删掉一个文件夹，里面的文件跟着消失；如果没有这条规则，数据库里会留下一堆「找不到家」的孤儿条目，查询时全是麻烦。

这个参数**必须显式写**。Django 2.0 起它就是必填的——框架逼着你在删数据之前想清楚后果，这本身就是一种安全设计。

### 2.5 一次请求的旅程：URL → 视图 → 模板 ★

这是本单元最难的部分，也是 Django 的命脉。用户每敲一次网址，都发生下面这一串事：

```text
浏览器输入 http://127.0.0.1:8000/topics/
  │
  │ ① 请求到达 Django 服务器
  ▼
ll_project/urls.py                项目总前台
  │ ② 逐个比对 urlpatterns：'' 开头的都归 learning_logs 管
  │    path('', include('learning_logs.urls')) —— 转手
  ▼
learning_logs/urls.py             应用分前台
  │ ③ 比对 urlpatterns：'topics/' 命中 path('topics/', views.topics, name='topics')
  │    调用视图函数；如果 URL 里带 <int:topic_id>，顺手把数字抠出来当参数
  ▼
learning_logs/views.py            厨师
  │ ④ topics(request) 向数据库要数据：Topic.objects.order_by('date_added')
  │    把数据装进 context 字典
  ▼
templates/learning_logs/topics.html   摆盘
  │ ⑤ render(request, 模板, context) 把数据填进模板的坑里
  ▼
一串 HTML（HTTP 响应）→ 浏览器渲染成你看到的页面
```

每个文件「是干什么的、改了它会影响什么」，一张表说清：

| 文件 | 角色 | 改坏了会怎样 |
|---|---|---|
| `ll_project/urls.py` | 总路由，把请求分流给各 app | 整个网站 404 |
| `learning_logs/urls.py` | 本 app 的路由表，URL → 视图函数 | 某个页面打不开 / NoReverseMatch |
| `learning_logs/views.py` | 业务逻辑，查数据、装 context | 页面数据不对或报错 |
| `templates/learning_logs/*.html` | 页面长相 | 长相不对或变量显示为空 |

`path()` 接受三个实参：**URL 模式字符串**（比如 `'topics/<int:topic_id>/'`）、**要调用的视图函数**、**这个模式的名字**（`name='topic'`）。名字是给 `{% url %}` 用的——以后改 URL 结构，只需改 `urls.py` 一处，所有链接自动更新，这正是模板标签生成 URL 的价值。

`path()` 里那些 `<int:topic_id>` 在匹配时会被翻成正则，所以「谁先谁后」有讲究。把匹配表写成纯 Python 跑一遍，你能亲眼看到「第一个命中的赢」和「`/topics/abc/` 为什么 404」：

```python
# URL 匹配表：urlpatterns 的顺序为什么不能乱
import re

# path('topics/<int:topic_id>/', ...) 在匹配时会被翻成这样的正则
URLPATTERNS = [
    (r"^$", "index"),
    (r"^topics/$", "topics"),
    (r"^topics/(?P<topic_id>\d+)/$", "topic"),
    (r"^new_topic/$", "new_topic"),
    (r"^topics/(?P<topic_id>\d+)/new_entry/$", "new_entry"),
]


def resolve(path):
    """逐个比对，第一个命中的就是赢家；一个都不中就 404。"""
    path = path.lstrip("/")          # ★ urlpatterns 里的模式不带开头的斜杠
    for pattern, view in URLPATTERNS:
        match = re.match(pattern, path)
        if match:
            return view, match.groupdict()
    return "404", {}


for path in ["/", "/topics/", "/topics/3/", "/topics/3/new_entry/",
             "/topics/abc/", "/new_topic/", "/admin/"]:
    view, kwargs = resolve(path)
    extra = f"，参数 {kwargs}" if kwargs else ""
    print(f"{path:<24}-> {view}{extra}")
```

这段跑出来是：`/topics/3/` 命中 `topic` 并带出 `{'topic_id': '3'}`，`/topics/3/new_entry/` 命中 `new_entry`（`^topics/\d+/$` 末尾的 `$` 锚住了行尾，所以不会把它误吞），`/topics/abc/` 和 `/admin/` 都落到 `404`。**模式末尾的 `$` 和「更具体的写前面」是最省事的两条纪律**，Django 的 `include()` 也是同一个道理：总路由先按前缀分流，再进各 app 的匹配表。

### 2.6 模板语法：`{{ }}`、`{% for %}` 与 `{% url %}`

模板里只有三样东西要记：

| 写法 | 名字 | 作用 | 例子 |
|---|---|---|---|
| `{{ topic.text }}` | 模板变量 | 把 context 里的数据填进来 | 双花括号，不会出现在网页里 |
| `{% for topic in topics %}` | 模板标签 | 一小段代码，循环 / 判断 | 花括号加百分号 |
| `{% url 'learning_logs:topic' topic.id %}` | 模板标签 | 按名字生成 URL | 命名空间写法 |

循环必须以 `{% endfor %}` 显式收尾——模板不靠缩进判断边界，忘了写 `{% endfor %}` 是高频错误。`{% empty %}` 是贴心设计：列表为空时显示什么，一句话搞定，不用在视图里写 if。

```html
{% for topic in topics %}
  <li>{{ topic.text }}</li>
{% empty %}
  <li>还没有添加任何主题。</li>
{% endfor %}
```

过滤器用竖线 `|` 表示，在渲染过程中修改变量的值：`{{ entry.date_added|date:'M d, Y H:i' }}` 把时间戳格式化成「May 20, 2022 03:33」，`{{ entry.text|linebreaks }}` 把条目里的换行转换成浏览器认的格式。

`'learning_logs:topic'` 里的**冒号前是命名空间**（来自 `urls.py` 里的 `app_name`，相当于 URL 模式们的「姓」），冒号后是模式名（「名」）。两个 app 都有一叫 `index` 的页面也不打架，靠姓区分。顺带记住教材的提醒：模板里写的是 `topic.id`（取对象的 ID 值），而视图函数里的形参叫 `topic_id`（装这个值的变量）——用错就是 NoReverseMatch。

过滤器看着神秘，其实每个都能在 Python 里找到等价物——**它们只改「怎么显示」，不改 context 里的原始值**：

```python
# 模板过滤器 |date 的等价物：python 里就是 strftime
from datetime import datetime

entry = {"date_added": datetime(2022, 5, 20, 3, 33),
         "text": "今天学了 Django 模板\n第二行要换行"}

print("模板里写 {{ entry.date_added|date:'M d, Y H:i' }}")
print("  python 等价：", entry["date_added"].strftime("%b %d, %Y %H:%M"))
print("  对照：%b 是缩写月份（May），%B 是全称（May 在这里一样，December 才有差别）")

print("\n模板里写 {{ entry.text|linebreaks }}")
print("  python 等价：", "<p>" + entry["text"].replace("\n\n", "</p><p>")
      .replace("\n", "<br>") + "</p>")

print("\n模板里写 {{ entry.text|truncatewords:4 }}")
print("  等价：", " ".join(entry["text"].split()[:4]) + " …")

print("\n这些过滤器都只改「显示」，不改 context 里的原始值：")
print("  原始 date_added 还是：", entry["date_added"])
```

`|date` 用的格式码和单元 16 的 `strftime` **完全同一套**（`%Y` `%m` `%d` `%H` `%M`）；`|linebreaks` 就是「把换行变成 `<br>`、把空行变成分段」；`|truncatewords:4` 取前 4 个词。想验证一个过滤器到底做了什么，最直接的办法仍是「查看网页源代码」——它输出的就是 HTML 字符串。

### 2.7 模板继承与 404：别每个页面重复写导航栏 ★

每个页面都有导航栏。如果每个 `.html` 都手写一遍，改一次导航要翻遍所有文件、漏一个就是一个坏链接——这是「复制粘贴式开发」的经典悲剧。Django 的解法是**模板继承**：把公共骨架写进父模板 `base.html`，挖好「坑」；子模板只管填自己那一亩三分地。

类比：`base.html` 是开发商的精装房——水电、地板、墙面全装好，留几个空房间；子模板是业主，只往空房间里摆自己的家具。

```html
{% block content %}{% endblock content %}
```

这个「坑」叫 `content`。子模板第一行必须用 `{% extends %}` 认祖归宗：

```html
{% extends 'learning_logs/base.html' %}

{% block content %}
  <p>这个页面独有的内容都放在这里。</p>
{% endblock content %}
```

**404 处理**：视图里 `Topic.objects.get(id=topic_id)` 遇到不存在的 ID 会抛异常，直接变成 500 服务器错误页——很难看，也暴露了内部信息。教材在第 19 章的正式做法是先判断归属、再 `raise Http404`；这里先给一个等价的一步到写法：

> 教材未涉及，补充说明：Django 还提供快捷函数 `get_object_or_404(Topic, id=topic_id)`——取到就返回对象，取不到就自动抛 404。它和「先 `get()` 再手动判断」效果一样，只是更短。本课程后续统一用教材的写法，你知道有这把扳手即可。

---

## 三、可运行代码示例

> 示例 1 ~ 3 是纯 Python 模拟程序，直接 `python 文件名.py` 就能运行——目的是在碰 Django 之前，先把「外键」「请求链路」「模板继承」三个抽象概念在屏幕上跑起来；示例 4 ~ 8 是学习笔记项目的真实文件，需在 Django 项目环境里运行（每块都标了文件路径，全部完整、无省略）。

### 示例 1：用纯 Python 看懂外键和级联删除

```python
# fk_simulation.py —— 模拟 models.ForeignKey 背后发生的事

class Topic:
    """主题：相当于数据库表 learning_logs_topic 里的一行。"""

    def __init__(self, topic_id, text):
        self.id = topic_id
        self.text = text

    def __str__(self):
        return self.text


class Entry:
    """条目：topic 这一列「指向」某个主题——这就是外键。"""

    def __init__(self, entry_id, topic, text):
        self.id = entry_id
        self.topic = topic          # 外键：记住自己属于哪个主题
        self.text = text

    def __str__(self):
        return self.text[:20]


# ===== 造数据：两个主题、三条条目（一对多）=====
python_topic = Topic(1, "Python")
django_topic = Topic(2, "Django")
entries = [
    Entry(1, python_topic, "列表推导式很好用"),
    Entry(2, python_topic, "生成器可以省内存"),
    Entry(3, django_topic, "先建虚拟环境再装包"),
]

print("删除前，所有条目：")
for entry in entries:
    print(f"  条目{entry.id}: {entry} -> 属于《{entry.topic}》")


# ===== 模拟 on_delete=models.CASCADE（级联删除）=====
def delete_topic_cascade(topic, all_entries):
    """级联删除：剔除该主题，以及挂在它下面的全部条目。"""
    return [e for e in all_entries if e.topic is not topic]


entries = delete_topic_cascade(python_topic, entries)
print("\n删除《Python》后（CASCADE 生效），剩下的条目：")
for entry in entries:
    print(f"  条目{entry.id}: {entry} -> 属于《{entry.topic}》")

# ===== 对比：没有 on_delete 规则会怎样 =====
orphan = Entry(99, python_topic, "这条的作者已经没人认领了")
print(f"\n假如没有级联删除，数据库里会留下孤儿：")
print(f"  条目{orphan.id}: {orphan} -> 指向的主题《{orphan.topic}》已不存在")
print("  => 显示、查询时全是麻烦，所以 on_delete 必须显式写清楚")
```

### 示例 2：用纯 Python 模拟「URL → 视图 → 模板」请求链路

```python
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
```

### 示例 3：用纯 Python 模拟模板继承

```python
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
```

### 示例 4：`learning_logs/models.py`（项目文件，完整版）

```python
# learning_logs/models.py —— 学习笔记的数据模型
from django.db import models


class Topic(models.Model):
    """用户学习的主题（一对多关系里的「一」）。"""

    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """在管理网站和 shell 里显示主题时，返回 text。"""
        return self.text


class Entry(models.Model):
    """学到的有关某个主题的具体知识（一对多关系里的「多」）。"""

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "entries"      # 否则管理网站会显示难看的 Entrys

    def __str__(self):
        """条目可能很长，只截取前 50 个字符显示。"""
        return f"{self.text[:50]}..."
```

### 示例 5：`learning_logs/admin.py` 与 Django shell 查数据

```python
# learning_logs/admin.py —— 向管理网站注册模型（不注册，后台就看不到）
from django.contrib import admin

from .models import Topic, Entry

admin.site.register(Topic)
admin.site.register(Entry)
```

```bash
# 对应的终端操作：建超级用户、迁移、进 shell 查数据
python manage.py makemigrations learning_logs
python manage.py migrate
python manage.py createsuperuser
python manage.py shell
```

```text
Django shell 会话（python manage.py shell 之后逐行输入）：

>>> from learning_logs.models import Topic
>>> Topic.objects.all()
<QuerySet [<Topic: Chess>, <Topic: Rock Climbing>]>
>>> for topic in Topic.objects.all():
...     print(topic.id, topic)
...
1 Chess
2 Rock Climbing
>>> t = Topic.objects.get(id=1)
>>> t.entry_set.all()          # 通过外键反向查出该主题的所有条目
<QuerySet [<Entry: The opening is the first part of the game...>]>
>>> exit()                     # 或按 Ctrl+D 退出（Windows 先 Ctrl+Z 再回车）
```

### 示例 6：两个 `urls.py`（项目文件，完整版）

```python
# learning_logs/urls.py —— 应用程序自己的路由表
"""定义 learning_logs 的 URL 模式"""

from django.urls import path

from . import views

app_name = "learning_logs"          # 命名空间：模板里 {% url 'learning_logs:index' %} 靠它

urlpatterns = [
    # 主页
    path("", views.index, name="index"),
    # 显示所有主题的页面
    path("topics/", views.topics, name="topics"),
    # 特定主题的详细页面
    path("topics/<int:topic_id>/", views.topic, name="topic"),
]
```

```python
# ll_project/urls.py —— 项目的总路由：把 learning_logs 开头的请求转给 app
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("learning_logs.urls")),
]
```

### 示例 7：`learning_logs/views.py`（项目文件，完整版）

```python
# learning_logs/views.py —— 学习笔记的视图函数
from django.shortcuts import render

from .models import Topic


def index(request):
    """学习笔记的主页。"""
    return render(request, "learning_logs/index.html")


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
```

### 示例 8：四份模板（项目文件，完整版）

```html
<!-- templates/learning_logs/base.html —— 父模板：所有页面共享的骨架 -->
<p>
  <a href="{% url 'learning_logs:index' %}">Learning Log</a> -
  <a href="{% url 'learning_logs:topics' %}">Topics</a>
</p>

{% block content %}{% endblock content %}
```

```html
<!-- templates/learning_logs/index.html —— 主页 -->
{% extends "learning_logs/base.html" %}

{% block content %}
  <p>Learning Log helps you keep track of your learning, for any topic
  you're interested in.</p>
{% endblock content %}
```

```html
<!-- templates/learning_logs/topics.html —— 显示所有主题 -->
{% extends "learning_logs/base.html" %}

{% block content %}

  <p>Topics</p>

  <ul>
    {% for topic in topics %}
      <li>
        <a href="{% url 'learning_logs:topic' topic.id %}">{{ topic.text }}</a>
      </li>
    {% empty %}
      <li>No topics have been added yet.</li>
    {% endfor %}
  </ul>

{% endblock content %}
```

```html
<!-- templates/learning_logs/topic.html —— 显示特定主题及其条目 -->
{% extends "learning_logs/base.html" %}

{% block content %}

  <p>Topic: {{ topic.text }}</p>

  <p>Entries:</p>
  <ul>
    {% for entry in entries %}
      <li>
        <p>{{ entry.date_added|date:'M d, Y H:i' }}</p>
        <p>{{ entry.text|linebreaks }}</p>
      </li>
    {% empty %}
      <li>There are no entries for this topic yet.</li>
    {% endfor %}
  </ul>

{% endblock content %}
```

---

## 四、动手练习

### 基础档

**练习 18-1【从零跑通第一个页面】**
按顺序执行，每一步记录结果：
1. 建目录 `learning_log`，创建虚拟环境 `ll_env`，激活（确认提示符出现 `(ll_env)`）
2. `pip install --upgrade pip` 后安装 Django
3. `django-admin startproject ll_project .`——**千万别忘了末尾的句点**，然后 `ls` 看看创建了什么
4. `python manage.py startapp learning_logs`，并把 app 注册进 `INSTALLED_APPS`
5. `python manage.py migrate`，再 `python manage.py runserver`
6. 浏览器打开 `http://127.0.0.1:8000/`，看到 Django 的火箭欢迎页
验收点：能说清 `ll_env`、`ll_project`、`learning_logs` 三层各自是什么；知道 `db.sqlite3` 是哪一步产生的。

**练习 18-2【教材练习 18.2：简短的条目】**
教材原题：当前 `Entry.__str__()` 总在末尾加省略号。请加一条 `if` 语句，**仅当条目长度超过 50 个字符时**才加省略号。改完后重新迁移，用管理网站添加一个不超过 50 个字符的条目，确认显示时不带省略号。
提示：改的是 `models.py`，改完必须重走三步曲的后两步。

**练习 18-3【教材练习 18.4：比萨与配料】**
新建项目 `pizzeria_project`（记得末尾句点）和 app `pizzas`：
1. 定义模型 `Pizza`：字段 `name`（存储比萨名）
2. 定义模型 `Topping`：字段 `pizza`（关联到 `Pizza` 的外键）和 `name`（配料名）
3. 向管理网站注册两个模型，用后台添加几个比萨和配料
4. 用 Django shell 查询：打印所有比萨，以及某张比萨的所有配料
验收点：外键方向别写反——是「配料指向比萨」，不是反过来。

### 进阶档

**练习 18-4【手写迷你模板引擎】**
不借助 Django，写一个迷你渲染器 `mini_render(template, context)`，要求：
1. 支持 `{{ 变量名 }}` 替换为 context 里对应的值
2. 支持 `{% for x in 列表 %}...{% endfor %}` 单层循环，循环体内可用 `{{ x }}`
3. 用 `{"topics": ["Python", "Django", "Git"]}` 和对应模板测试，输出正确 HTML
提示：可以先用字符串 `find`/切片定位标签位置，循环部分把循环体重复拼接。写完对比示例 2、3 的思路。

**练习 18-5【给学习笔记加「关于」页面】**
新增一个 `/about/` 页面，改三个文件：
1. `learning_logs/urls.py`：加 `path("about/", views.about, name="about")`
2. `learning_logs/views.py`：加 `about(request)` 视图，渲染 `"learning_logs/about.html"`
3. 新建 `templates/learning_logs/about.html`：继承 `base.html`，写一两句项目介绍
4. 顺手在 `base.html` 导航里加上它的链接
验收点：浏览器打开 `/about/` 正常显示，且导航链接可点击跳转。

---

## 五、参考答案

### 参考答案 18-1

```bash
# ===== 1）建目录 + 虚拟环境 =====
mkdir learning_log
cd learning_log
python -m venv ll_env

# ===== 2）激活（按系统三选一）=====
source ll_env/bin/activate          # macOS / Linux
ll_env\Scripts\activate             # Windows 命令行
ll_env\Scripts\Activate             # Windows PowerShell（A 大写）
# 激活成功的标志：提示符变成 (ll_env)learning_log$

# ===== 3）装 Django =====
(ll_env)learning_log$ pip install --upgrade pip
(ll_env)learning_log$ pip install django

# ===== 4）建项目（末尾句点是重点）=====
(ll_env)learning_log$ django-admin startproject ll_project .
(ll_env)learning_log$ ls
# ll_env  ll_project  manage.py

# ===== 5）建应用 + 注册学籍 =====
(ll_env)learning_log$ python manage.py startapp learning_logs
# 然后编辑 ll_project/settings.py，把 'learning_logs' 加进 INSTALLED_APPS

# ===== 6）建数据库 + 跑起来 =====
(ll_env)learning_log$ python manage.py migrate
# 执行后目录里会出现 db.sqlite3——这就是数据库本体
(ll_env)learning_log$ python manage.py runserver
# 浏览器访问 http://127.0.0.1:8000/ 看到火箭页即成功
# 端口被占用时：python manage.py runserver 8001
```

自查三个问题：`ll_env` 是工具间（装 Django 的地方）；`ll_project` 是项目配置的家（settings.py、总 urls.py 住这）；`learning_logs` 是干活的 app（models、views 住这）。`db.sqlite3` 由 `migrate` 产生。

### 参考答案 18-2

```python
# learning_logs/models.py —— Entry.__str__() 仅在超过 50 字符时加省略号
from django.db import models


class Topic(models.Model):
    """用户学习的主题"""

    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class Entry(models.Model):
    """学到的有关某个主题的具体知识"""

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "entries"

    def __str__(self):
        """条目超过 50 个字符时才加省略号。"""
        if len(self.text) > 50:
            return f"{self.text[:50]}..."
        return self.text
```

```bash
# 改完模型必须重走后两步，否则数据库不认
python manage.py makemigrations learning_logs
python manage.py migrate
```

注意：这次只改了 `__str__()`（一个普通方法，不涉及数据库列），`makemigrations` 会提示「No changes detected」——这是正常的，方法层面的修改本来就不需要迁移。

### 参考答案 18-3

```python
# pizzas/models.py —— 比萨与配料（多对一）
from django.db import models


class Pizza(models.Model):
    """一种比萨。"""

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Topping(models.Model):
    """比萨上的一种配料，通过外键关联到特定比萨。"""

    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
```

```python
# pizzas/admin.py —— 注册两个模型
from django.contrib import admin

from .models import Pizza, Topping

admin.site.register(Pizza)
admin.site.register(Topping)
```

```bash
# 终端操作
python manage.py makemigrations pizzas
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver      # 访问 /admin/ 添加数据
```

```text
Django shell 验证查询：

>>> from pizzas.models import Pizza, Topping
>>> for pizza in Pizza.objects.all():
...     print(pizza.name)
...     for topping in pizza.topping_set.all():   # 外键的反向查询
...         print("  -", topping.name)
...
Hawaiian
  - pineapple
  - Canadian bacon
Meat Lovers
  - sausage
```

方向判断口诀：**外键写在「多」的那一边**。N 个配料属于 1 张比萨，所以 `ForeignKey` 定义在 `Topping` 里，指向 `Pizza`。

### 参考答案 18-4

```python
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
```

思路说明：先循环后变量——循环体里也可能嵌着 `{{ x }}`，等循环展开完再统一替换最省心。这正是 Django 模板引擎的简化版工作原理。

### 参考答案 18-5

```python
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
```

```python
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
```

```html
<!-- templates/learning_logs/about.html —— 继承父模板，只写独有内容 -->
{% extends "learning_logs/base.html" %}

{% block content %}
  <h1>关于学习笔记</h1>
  <p>Learning Log 是一个在线笔记应用，帮助你记录感兴趣的主题，
  以及学习每个主题过程中的心得。</p>
{% endblock content %}
```

```html
<!-- templates/learning_logs/base.html —— 导航里加上 about 链接 -->
<p>
  <a href="{% url 'learning_logs:index' %}">Learning Log</a> -
  <a href="{% url 'learning_logs:topics' %}">Topics</a> -
  <a href="{% url 'learning_logs:about' %}">About</a>
</p>

{% block content %}{% endblock content %}
```

---

## 六、常见错误清单（务必逐条自查）

### 错误 1：★ 忘了激活虚拟环境

症状：`ModuleNotFoundError: No module named 'django'`；或者 Django 装是装上了，但换个终端就消失。诊断方法只有一个——**看提示符前面有没有 `(ll_env)`**。没有就重新激活：`source ll_env/bin/activate`（Windows 用 `ll_env\Scripts\activate`）。记住：每开一个新终端，就要重新激活一次。

### 错误 2：★ 搞混 `learning_log/`、`ll_project/`、`learning_logs/`

三个名字长得像，角色完全不同：`learning_log/` 是你的工作目录（`manage.py` 在这），`ll_project/` 是项目配置的家（`settings.py`、总 `urls.py` 在这），`learning_logs/` 是干活的 app（`models.py`、`views.py` 在这）。**改错文件是新手最贵的浪费**——在 `ll_project` 里找 `models.py` 当然找不到，因为模型在 `learning_logs` 里。拿不准就 `ls` 看一眼。

### 错误 3：改了 `models.py` 不迁移

加完字段直接刷新网页，报 `OperationalError: no such table` 或「no such column」。原因：只改了图纸没施工。记住三步曲一个都不能少：改 `models.py` → `makemigrations` → `migrate`。反过来也要警惕：`makemigrations` 之后忘了 `migrate`，同样是图纸没施工。

### 错误 4：新 app 忘了在 `INSTALLED_APPS` 登记

症状：`migrate` 不给你的模型建表；管理网站里看不到模型；报 `LookupError: No installed app with label 'xxx'`。类比：新生不来注册学籍，学校花名册上就没这人，食堂不给他开饭。`startapp` 之后第一件事，就是去 `settings.py` 登记。

### 错误 5：`startproject` 末尾忘了写句点

`django-admin startproject ll_project`（没有 `.`）会多套一层目录，`manage.py` 被埋进子目录，部署时各种配置问题。教材特意用「注意」框强调：**千万别忘了这个句点**。真忘了也别慌——删掉刚生成的目录（保留 `ll_env`），带上句点重跑。

### 错误 6：模板里 `{% url %}` 写错

`NoReverseMatch: Reverse for 'index' not found`——十有八九是漏了命名空间。正确写法是 `{% url 'learning_logs:index' %}`（app 名 + 冒号 + URL 模式名）。另外注意教材的提醒：模板里用对象的 `topic.id` 取 ID 值，视图里的形参叫 `topic_id`，两者别混。

---

## 七、本单元验收自测

**1. 简答题**：虚拟环境解决什么问题？三条激活命令是什么？怎么判断激活成功了？
> **要点**：不同项目依赖不同版本的包，全塞进一个 Python 会互相冲突；虚拟环境给每个项目一间独立的「工具间」，包装在本环境内、只在本环境有效。激活命令：macOS/Linux 用 `source ll_env/bin/activate`，Windows 命令行用 `ll_env\Scripts\activate`，PowerShell 可能要写 `Activate`。激活成功的标志是提示符前出现 `(ll_env)`。新建 app、装包之前，第一件事就是确认这个前缀在不在。

**2. 简答题**：解释「模型 → 迁移 → 数据库」三步曲，`makemigrations` 和 `migrate` 各做什么？
> **要点**：① 改 `models.py`，告诉 Django 想要什么数据结构；② `makemigrations` 把改动翻译成迁移文件（`migrations/0001_initial.py`），这是**数据库的施工图纸**，记录这次要建什么表、加什么列；③ `migrate` 照图纸真正修改数据库。只画图不施工（漏了 `migrate`）会报 `no such table`；反过来，不画图就想施工是行不通的——没有迁移文件，Django 不知道你要怎么改。

**3. 判断题**：`Topic.objects.order_by("date_added")` 返回的是列表，所以在模板里要先用 `|length` 才能遍历。
> **要点**：错误。它返回的是查询集（queryset），行为像列表——可以直接遍历、可以切片、可以传给模板。模板里 `{% for topic in topics %}` 不需要任何预处理。（教材未涉及，补充说明：查询集还是惰性的，定义时不一定马上查数据库，真正被迭代到数据时才查。）

**4. 简答题**：画出用户访问 `/topics/` 时，Django 内部发生的完整链路。
> **要点**：浏览器发请求 → `ll_project/urls.py` 的 `urlpatterns` 比对，`''` 前缀的请求经 `include("learning_logs.urls")` 转手 → `learning_logs/urls.py` 里 `'topics/'` 命中 `path('topics/', views.topics, name='topics')` → 调用 `views.py` 的 `topics(request)`，执行 `Topic.objects.order_by("date_added")` 查库，把结果装进 `context` 字典 → `render(request, "learning_logs/topics.html", context)` 把数据填进模板 → 返回 HTML 响应，浏览器渲染。

**5. 改错题**：下面代码想让「主题列表页」工作，有 3 处错误，找出来并改正。

```python
# INTENTIONALLY-BROKEN 演示用：3 处错误，见下方解析
def topics(request):
    """显示所有主题"""
    topics = Topic.objects.all()
    context = {topics: topics}
    return render("learning_logs/topics.html", context)
```

> **要点**：错误一，`context = {topics: topics}` 把变量当键名了，字典的键必须是字符串——应为 `context = {"topics": topics}`，模板里才能用 `{% for topic in topics %}` 按这个名字取数据；错误二，`render()` 少了第一个实参 `request`——应为 `render(request, "learning_logs/topics.html", context)`，Django 的 `render()` 签名是 `render(request, template_name, context)`；错误三（潜在），`Topic.objects.all()` 虽然能跑，但主题页应该按添加时间排序，规范写法是 `Topic.objects.order_by("date_added")`，让老主题在前、新主题在后。

**6. 简答题**：`on_delete=models.CASCADE` 是什么意思？如果删掉一个 Topic，会发生什么？
> **要点**：外键字段 `topic = models.ForeignKey(Topic, on_delete=models.CASCADE)` 表达「条目属于主题」的多对一关系；`on_delete` 回答「主题没了，条目怎么办」。`CASCADE` 是级联删除：删主题时，挂在它下面的所有条目一起删。类比删文件夹时里面的文件一起消失。不写这个参数 Django 直接报错——它逼你在删数据前想清楚后果。反向查询用 `topic.entry_set.all()`：通过外键关系拿到某个主题的所有条目。

---

## 本单元小结与产出检查

- [ ] 能不查资料说出虚拟环境解决什么问题，并写出三条激活命令
- [ ] 能画出 `learning_log/`、`ll_project/`、`learning_logs/` 的目录关系，说清各自住着什么文件
- [ ] 能默写三步曲：改 `models.py` → `makemigrations` → `migrate`，并解释迁移文件是什么
- [ ] 能画出「URL → 视图 → 模板」请求链路图，说清 `render()` 的三个实参
- [ ] 能写出 `{% for %}`、`{{ }}`、`{% url 'learning_logs:xxx' %}`、`{% block content %}` 四种模板语法
- [ ] 能解释 `on_delete=models.CASCADE` 与外键的反向查询 `topic.entry_set.all()`
- [ ] 练习 18-1、18-4 已跑通

**下一单元预告**：单元 19 讲「用户账户」——给学习笔记装上「人」的维度：用 `ModelForm` 让用户不进后台就能添加主题和条目，用 Django 自带的登录/注销视图和自己写的注册页面搭好身份验证，最重要的是学会 `@login_required` 和 `filter(owner=request.user)`，守住「每个用户只能看见自己的数据」这条 Web 开发的安全红线。你现在这个项目还只有你一个用户，下一单元之后，任何人都能注册、每个人都有一间自己的上锁房间。
