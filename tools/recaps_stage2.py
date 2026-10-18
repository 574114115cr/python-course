# -*- coding: utf-8 -*-
"""阶段 2（第 65–111 节）的复盘与讲评内容。

与 recaps.py / reviews.py 分开，避免单文件过长。编号与全部课程一致（1~111）。
"""

# ── 第 65 节 = 单元 12 第 1 节：开课准备 ──
OPENING = [
    "阶段 2 的定位和阶段 1 不同：那里学的是<b>语法</b>，这里学的是<b>做项目</b>。"
    "三本教材项目——外星人入侵、数据可视化、学习笔记——都是几百行、多文件、有第三方依赖的真实程序。",
    "<b>先装好三个库</b>：<code>pip install pygame matplotlib plotly requests</code>，"
    "后面单元 12–17 都要用。",
    "阶段 2 的核心变化：你的代码从<b>一个文件</b>变成<b>一个项目目录</b>。"
    "从今天起，每节课都要问一句「这个文件在整个项目里的位置是什么」。",
]

# ── 复盘：回顾上一节 ──
RECAP = {
    65: [
        "阶段 1 你写的是几十行的单文件脚本；阶段 2 是几百行、分多个文件、有第三方依赖的项目。",
        "三个阶段 2 项目分别对应教材的三大板块：Pygame（12–14 章）、数据可视化（15–17 章）、Django（18–20 章）。",
        "阶段 1 的每个单元在这里都有用：函数是模块的基础，类是 Pygame 精灵和 Django 模型的基础，"
        "文件与异常是 JSON 存盘的基础，pytest 是收尾验收的基础。",
        "<b>阶段 2 的统一工程流程</b>：读需求 → 自己先拆解（别急着抄）→ 查官方文档 → 编码 → git 提交 → 写 README → 重构。",
    ],
    66: [
        "Pygame 程序的主循环是 <code>while True</code>，每轮做四件事："
        "<b>监听事件 → 更新飞船 → 更新屏幕 → 控制帧率</b>。",
        "<code>pygame.event.get()</code> 返回的是事件队列；<code>KEYDOWN</code> 是按键按下，"
        "<code>QUIT</code> 是点右上角关窗。",
        "<code>self.clock.tick(60)</code> 必须在循环最后一行——它不是「开始」，是「这一帧到此为止，等够时间再进下一帧」。",
    ],
    67: [
        "游戏是<b>事件驱动</b>的：程序不主动问你要什么，而是等事件发生再去响应。",
        "帧率锁 60 表示「每秒最多 60 帧」。不锁的话，你的电脑和别人的电脑速度完全不同。",
        "背景色和窗口大小属于「会变的设置」，不该散落在代码各处——下一节就要把它们收进一个类。",
    ],
    68: [
        "<code>Settings</code> 类的意义：把会变的数值集中管理。改窗口大小、飞船速度、颜色，只动这一个文件。",
        "<code>screen_rect = self.screen.get_rect()</code> 是一个 Rect 对象，有 <code>.top/.bottom/.left/.right</code> 四个属性。",
        "飞船类只负责「我是谁、我能做什么」；「世界有多大、速度多快」由 Settings 决定——这是职责分离。",
    ],
    69: [
        "<code>moving_right</code> / <code>moving_left</code> 两个布尔标志位，是「按住持续移动」的标准做法："
        "按下设 True、松开设 False，每帧按标志更新位置。",
        "边界限制靠 <code>screen_rect</code>：<code>if self.rect.right &gt;= self.settings.screen_rect.right:</code> "
        "——注意飞船中心到了边缘就该停，所以要减去半个飞船宽度。",
        "<code>pygame.key.get_pressed()</code> 和 <code>KEYDOWN</code> 事件是两种不同的查键方式，别混用。",
    ],
    70: [
        "重构的核心：主循环只留「调用清单」，具体逻辑下沉到 <code>_check_events()</code> 和 <code>_update_screen()</code>。",
        "下划线开头的 <code>_check_events</code> 表示「这是内部方法，不建议外部直接调用」——这是 Python 的约定。",
        "重构不是「重写」，是<b>把长函数拆短、把重复合并</b>，行为必须完全不变。改完要跑一遍确认没坏。",
    ],
    71: [
        "编组 <code>Group</code> 和普通 list 的三点差别："
        "<code>add/remove/update/draw</code> 都自动、<code>copy()</code> 才能安全遍历、<code>remove</code> 收对象不收下标。",
        "★ 遍历时删除会漏删——必须遍历 <code>.copy()</code>、删除原件。这和阶段 1「遍历字典不能删键」是同一条红线。",
        "精灵 <code>Sprite</code> 有 <code>image</code>（图像）和 <code>rect</code>（位置矩形）两个核心属性。",
    ],
    72: [
        "<code>Bullet</code> 的三个必备：<code>update()</code> 往上移、<code>draw()</code> 画自己、超出屏幕就把自己删掉。",
        "限制子弹数量的原因：按住不放会一瞬间生成几百个子弹，程序卡死。这是真实项目里的性能考量。",
        "开火用 <code>pygame.sprite.Group</code> 存子弹，方便后面统一 update 和检测碰撞。",
    ],
    73: [
        "<code>_create_fleet()</code> 把「造一行 → 造多行」封装起来，是第一次真正的<b>函数化重构</b>。",
        "整队移动靠 <code>fleet_direction</code> 标志位（1 向右、-1 向左），"
        "任何一只外星人触边就<b>整队下移</b>并取反方向。",
        "边缘检测用 <code>&gt;=</code> / <code>&lt;=</code> 而不是 <code>==</code>：速度大于 1 时可能一步跨过精确坐标，"
        "<code>==</code> 会漏判，表现为「舰队飞出屏幕再也没回来」。",
    ],
    74: [
        "<code>pygame.sprite.groupcollide(bullets, aliens, True, True)</code> 返回一个列表："
        "命中的子弹对象和命中的外星人对象各一份。",
        "后两个 <code>True</code> 分别是 <code>kill_bullets</code> 和 <code>kill_aliens</code>。"
        "设成 <code>False</code> 会导致「外星人不消失、同一颗子弹反复加分」。",
        "<code>spritecollideany(ship, aliens)</code> 返回第一个碰撞的精灵，或 <code>None</code>——用来检测玩家被撞。",
        "游戏结束靠 <code>stats.game_active</code> 一个布尔值：主循环每轮检查它，为 False 就跳回待机。",
    ],
    75: [
        "★ 数据隔离的安全红线：<code>Topic.objects.filter(owner=request.user)</code>，"
        "写成 <code>.all()</code> 就会让每个用户看到所有人的数据。",
        "表单三段式：<code>form = ModelForm(data=request.POST)</code> → <code>form.is_valid()</code> → "
        "<code>obj = form.save(commit=False)</code> → <code>obj.owner = request.user</code> → <code>obj.save()</code>。",
        "<code>@login_required</code> 是不带括号的<b>装饰器</b>，写在 <code>def</code> 上一行；"
        "配合 <code>settings.LOGIN_URL</code> 决定踢到哪个页面。",
    ],
    76: [
        "游戏状态机：<code>game_active</code> 一个布尔值不够用，至少要区分 inactive / active / game over。",
        "Pygame 的文字不能直接画，必须 <code>font.render(text, True, color)</code> 渲染成 Surface 才能 <code>blit</code>。",
        "<code>Button</code> 类要持有 msg、rect、font、颜色——因为它得先把文字变成图像再算出按钮位置。",
    ],
    77: [
        "<code>prep_score()</code> 这类「准备图像」方法把<b>数据</b>和<b>显示</b>分开："
        "分数变化时只重新调用一次 prep，绘制时只 blit 一次。这是 UI 编程的通用套路。",
        "<code>round(self.score, -1)</code> 取整到十位；<code>\"{:,}\".format(1234)</code> 加千分位逗号。",
        "最高分和普通分数的区别：普通分数每次重开都清零，最高分要跨局保留——这是留给文件持久化的伏笔。",
    ],
    78: [
        "<code>speedup_scale</code> 用来调各类速度、<code>score_scale</code> 用来调加分倍率；"
        "两个都在 <code>initialize_dynamic_settings()</code> 里初始化。",
        "动态难度的正确流程：<code>increase_speed()</code> 先改 scale 再调用 initialize；"
        "顺序反了会让这局的设置被立刻重置。",
        "显示余下飞船数可以复用 <code>Ship</code> 类，只是换成小图像、放进另一个 Group——类的复用。",
    ],
    79: [
        "Matplotlib 和 Plotly 的分工：<b>matplotlib 出静态图（存 PNG），Plotly 出可交互 HTML</b>。",
        "推荐 <code>fig, ax = plt.subplots()</code>：<code>fig</code> 是整张画布，<code>ax</code> 是坐标系上的绘图区。",
        "<code>plt.plot()</code> 是过程式写法（全局状态），<code>ax.plot()</code> 是面向对象写法（状态在对象上）。"
        "多图时只有后者不会串。",
    ],
    80: [
        "<code>ax.scatter(x, y, s=, c=, alpha=)</code> 画散点图：<code>s</code> 是点大小、<code>c</code> 是颜色、"
        "<code>alpha</code> 是透明度。",
        "不设 <code>s</code> 时所有点看起来一样大——因为默认是一个固定值，数据越大差异越看不出来。",
        "<code>range(num_points)</code> 控制点数，<code>random.choice()</code> 造随机数；"
        "<code>random.seed()</code> 能让结果可复现。",
    ],
    81: [
        "★ <code>ax.axis([xmin, xmax, ymin, ymax])</code> 给坐标轴留边距。"
        "不调它，散点会贴边甚至被裁掉——这是 matplotlib 新手最高频的坑。",
        "颜色映射：<code>ax.scatter(..., c=y, cmap=plt.cm.Blues)</code>，"
        "数值大的点颜色深。这是把第三个维度映射到颜色的标准手法。",
        "<code>plt.savefig(\"x.png\", bbox_inches=\"tight\")</code> 保存；"
        "<code>bbox_inches=\"tight\"</code> 能避免标签被裁掉。",
    ],
    82: [
        "<code>RandomWalk</code> 类：<code>__init__</code> 造空的 <code>x_values/y_values</code>，"
        "<code>fill_walk()</code> 一步步填。",
        "★ <code>fill_walk()</code> 里的「拒绝原地不动」：<code>x_step</code> 和 <code>y_step</code> 不能同时为 0，"
        "否则路径会原地踏步，图上是一条直线。",
        "用 <code>ax.plot()</code> 画一条路径，用 <code>ax.scatter()</code> 高亮起点终点——同一个图上两种图元。",
    ],
    83: [
        "Plotly 的 <code>Die</code> 类：<code>roll()</code> 掷一次，<code>results.count(value)</code> 统计频次。",
        "<code>px.bar(x=, y=, color=)</code> 画直方图；<code>fig.write_html()</code> 存成可交互网页。",
        "同时掷两个骰子后分布更均匀——这是统计学上的大数定律，直观感受比讲公式有效。",
    ],
    84: [
        "<code>csv.reader</code> 逐行读；<code>reader.fieldnames</code> 拿表头；"
        "<code>reader.line_num</code> 拿行号。",
        "★ 表头位置不固定，要用 <code>enumerate</code> 找列的索引，不能硬编码列号——"
        "真实数据的列顺序随时会变。",
        "<code>datetime.strptime(\"2018-07-01\", \"%Y-%m-%d\")</code> 把字符串变日期对象，"
        "格式串要和数据严格对应。",
    ],
    85: [
        "★ 真实数据的三个坑：<b>缺失值、编码、表头不固定</b>。教材数据里就故意留了缺失值那一行。",
        "缺失值处理：<code>try / except</code> 跳过并打印警告，<b>不要静默跳过</b>——"
        "静默跳过的结果你永远不知道少了多少数据。",
        "<code>ax.plot(dates, highs, c=\"red\")</code> + "
        "<code>ax.fill_between(dates, highs, lows, facecolor=\"blue\", alpha=0.1)</code> 画温度区间带。",
    ],
    86: [
        "GeoJSON = 带地理坐标的 JSON：<code>data[\"features\"]</code> 是列表，"
        "每条有 <code>properties.mag</code>（震级）和 <code>geometry.coordinates</code>（坐标）。",
        "★ <code>coordinates[0]</code> 是<b>经度</b>、<code>coordinates[1]</code> 是<b>纬度</b>，顺序反了图就画到地球另一边。",
        "<code>px.scatter_geo(lat=, lon=, size=, color=, text=)</code> 画全球散点图，"
        "<code>text=</code> 是悬停提示。",
    ],
    87: [
        "API = 餐厅服务员：你按菜单点菜，他去厨房拿，你不必知道厨房怎么做。",
        "<code>requests.get(url)</code> 返回响应对象；<code>.status_code</code> 是状态码，"
        "<code>200</code> 成功、<code>403</code> 被拒、<code>404</code> 不存在、<code>429</code> 超速。",
        "★ <code>.json()</code> 把响应体转成 Python 字典——这是 API 调用最关键的一步，"
        "不转就只有一坨字符串你什么都做不了。",
    ],
    88: [
        "GitHub search API：<code>https://api.github.com/search/repositories?q=language:python&amp;sort=stars</code>。",
        "请求头 <code>Accept: application/vnd.github+json</code> 告诉 GitHub 你要 JSON 格式。",
        "★ 未认证每小时只有 60 次配额，用 <code>response.headers[\"X-RateLimit-Remaining\"]</code> 查剩余。"
        "写循环前先想清楚会不会超限。",
        "从 <code>response_dict[\"items\"]</code> 里取 <code>name</code> / <code>stargazers_count</code> / "
        "<code>html_url</code> / <code>description</code>。",
    ],
    89: [
        "<code>px.bar(x=repo_names, y=stars, hover_name=repo_names)</code> 画仓库条形图。",
        "<code>hover_data</code> 定制悬停内容；<code>marker</code> 定制颜色。",
        "★ 可点击链接要靠 <code>customdata</code> 传 URL，再在 <code>hovertemplate</code> 里用 "
        "<code>%{customdata}</code> 渲染成 <code>&lt;a&gt;</code> 标签。",
    ],
    90: [
        "两段式 API 调用：先取列表拿 id，再逐条取详情。"
        "<code>https://hacker-news.firebaseio.com/v0/topstories.json</code> → "
        "<code>item/{id}.json</code>。",
        "这类调用会发几十次请求，<b>必须</b>处理失败：某一条报错就跳过并计数，"
        "不能让它把整个程序带崩。",
        "★ 请求前适当 <code>time.sleep()</code> 限速——既保护自己也不给服务器添麻烦。",
    ],
    91: [
        "★ 虚拟环境 = 每个项目一间独立的「工具间」。不同项目可能需要不同版本的 Django，"
        "全局安装会互相打架。",
        "三条激活命令：Windows <code>.venv\\Scripts\\activate</code>、macOS/Linux <code>source .venv/bin/activate</code>。",
        "激活成功的标志：命令行前面出现 <code>(venv)</code>。创建：<code>python -m venv ll_env</code>。",
    ],
    92: [
        "Django 三层：<b>项目</b>（配置的家）→ <b>应用程序</b>（干活的）→ <b>MVT 三件套</b>（模型/视图/模板）。",
        "★ 每加一个应用都要去 <code>settings.py</code> 的 <code>INSTALLED_APPS</code> 登记，像新生注册学籍。",
        "★ 改模型的三步曲：改 <code>models.py</code> → <code>python manage.py makemigrations</code> → "
        "<code>python manage.py migrate</code>。少任何一步改动都不生效。",
        "迁移文件可以理解成数据库的「施工图纸」，改错了能回滚。",
    ],
    93: [
        "★ 一次请求的完整链路：浏览器发 URL → <code>urls.py</code> 找路由 → <code>views.py</code> 处理 → "
        "<code>render(request, \"x.html\", context)</code> → 模板渲染成 HTML 返回。",
        "视图的三件事：读请求参数（<code>request.GET</code>）、准备数据（查数据库）、传给模板。",
        "模板里的 <code>{% url 'app:name' arg %}</code> 带命名空间，避免不同应用的 URL 重名。",
    ],
    94: [
        "模板语法：<code>{{ 变量 }}</code> 插值、<code>{% for %}</code> 循环、<code>{% url %}</code> 生成链接。",
        "★ 模板继承：<code>base.html</code> 里挖 <code>{% block content %}{% endblock %}</code>，"
        "子模板 <code>{% extends \"base.html\" %}</code> 再填。不要每个页面重复写导航栏。",
        "<code>get_object_or_404(Model, pk=id)</code> 找不到就返回 404 页，"
        "而不是抛一个丑陋的服务器错误。",
    ],
    95: [
        "★ <code>request.user</code> 是 Django 给每个请求挂上的「当前用户」，"
        "未登录时是 <code>AnonymousUser</code>。",
        "★ 数据归属三段式：<code>form.save(commit=False)</code> 先拿未保存的对象、"
        "补上 <code>obj.owner = request.user</code>、再 <code>obj.save()</code>。"
        "少了中间那步，数据就不知道属于谁。",
        "<code>UserCreationForm</code> 自带用户名唯一性校验；自定义注册页要给它设模板。",
    ],
    96: [
        "★ 安全红线：<code>Topic.objects.filter(owner=request.user)</code>，"
        "写成 <code>.all()</code> 等于把所有人的数据公开。",
        "<code>@login_required</code> 是视图的门卫；<code>settings.LOGIN_URL</code> 告诉它踢到哪。",
        "注册视图里 <code>login(request, user)</code> 让用户注册后直接登录，少一步操作。",
    ],
    97: [
        "双重校验：既要检查「条目所属的主题属于当前用户」，也要检查「主题本身属于当前用户」，"
        "两层都要查才算安全。",
        "★ 校验失败的统一处理是 <code>return HttpResponseRedirect(...)</code> 跳走，"
        "而不是返回一个提示页——防止别人知道「这个 id 存在」。",
        "Django 自带 auth 的 URL 默认是 <code>/accounts/login/</code> 等，"
        "要留意 <code>LOGIN_URL</code> 配置是否对得上。",
    ],
    98: [
        "<code>django-bootstrap5</code>（注意不是 bootstrap4）：装上后在 <code>settings.py</code> 登记，"
        "模板里 <code>{% load django_bootstrap5 %}</code>。",
        "<code>{% bootstrap_form form %}</code> 一行把 Django 表单渲染成带样式的 HTML。",
        "改样式优先改 <code>base.html</code>，其他模板 <code>{% extends %}</code> 继承——"
        "改一处全部生效。",
    ],
    99: [
        "★ 部署 = 把代码放到一台<b>别人也能访问</b>的机器上跑，那台机器的环境和你本机不同。",
        "★ <code>requirements.txt</code> 是云环境的采购清单：<code>pip freeze &gt; requirements.txt</code>，"
        "云端靠它重建全部依赖。没有它部署必失败。",
        "云端唯一能依赖的就是这个文件，所以它必须进 git 仓库。",
    ],
    100: [
        "★ <code>.platform.app.yaml</code> 描述「应用怎么跑」，<code>.platform.routes.yaml</code> 描述「域名指向哪」。",
        "★ <code>platformshconfig</code> 解决「同一份代码怎么知道自己在本地还是云上」："
        "<code>if os.getenv(\"PLATFORM_APPLICATION\"):</code> 判断环境变量在不在。",
        "★ 三大部署坑：<code>ALLOWED_HOSTS</code> 不改直接 400；<code>DEBUG</code> 不关会泄漏信息；"
        "静态文件要 <code>collectstatic</code> 才能被服务。",
    ],
    101: {
        "items": [
            "★ 上线前逐条过检查清单：requirements.txt 齐不齐、ALLOWED_HOSTS 改没改、DEBUG 关没关、"
            "静态文件收没收集、错误页做了没。",
            "定制错误页：<code>handler404</code> / <code>handler500</code> 指向自己的模板，"
            "别人看到的是友好页面而不是技术细节。",
            "「继续开发」的双环境心智：本地改 → git commit → platform push，"
            "线上出问题就回滚版本，不是直接在线上改。",
        ],
        "summary": "上线不是推上去就完了——检查清单走完、错误页定制好，才算真的部署。",
    },
    102: [
        "阶段 2 三个项目分别练了三种能力：<b>Pygame 练交互与状态</b>、"
        "<b>数据可视化练数据处理与呈现</b>、<b>Django 练工程与安全</b>。",
        "工程流程七步：读需求 → 拆解 → 查文档 → 编码 → git 提交 → 写 README → 重构。"
        "前四步在阶段 1 练过，后三步是阶段 2 新增的。",
    ],
    103: [
        "★ 多文件项目的组织原则：<b>单文件不超过 300 行</b>；配置与逻辑分离；"
        "一个文件只管一件事。",
        "★ 密钥不进 git：密码、API key、数据库连接串一律走环境变量 + <code>.gitignore</code>。"
        "提交过就等于泄露，必须去平台改密钥。",
        "读陌生项目的顺序：先看 <code>README</code> → 看目录结构 → 找入口文件 → 跟着调用链走。",
    ],
    104: [
        "★ 关卡 2 五条硬指标里，最容易忽略的是「接手一个没写过的 500 行项目」。"
        "能读懂别人的结构，才算真的具备项目能力。",
        "「说清每个项目解决了什么问题、还能怎么扩展」——这条考的是<b>反思能力</b>，"
        "不是背结论。",
    ],
    105: [
        "阶段 2 收尾要拿出的是<b>能给人看的东西</b>：仓库里三个项目、公网上一个网站、"
        "一份写得清楚的学习总结。",
        "下一步四个方向：深 Web（REST / 前端）、深数据（pandas / numpy）、"
        "深自动化与爬虫、深测试与工程化。每条都要先有项目再学框架。",
    ],
    106: [
        "★ 安全红线的完整链条：<code>@login_required</code> 挡住未登录 → "
        "<code>filter(owner=request.user)</code> 挡住跨用户 → 双重校验挡住跨用户改条目。",
        "部署三件套：requirements.txt（依赖清单）、两个 yaml（怎么跑 + 路由怎么指）、"
        "settings.py 的环境判断分支。",
        "★ 上线检查清单：ALLOWED_HOSTS、DEBUG、collectstatic、错误页——少一条就有坑。",
    ],
    107: [
        "★ 关卡 2 五条里最容易忽略的是「接手一个没写过的 500 行项目」。"
        "能读懂别人的结构，才算真的具备项目能力。",
        "「说清每个项目解决了什么问题、还能怎么扩展」考的是<b>反思能力</b>，不是背结论。",
        "统一要求四条：单文件 ≤300 行、pytest ≥8 条、README 说清怎么装怎么跑、推到公开仓库。",
    ],
    108: [
        "★ 阶段 2 的终点不是「学完了 20 章」，而是「能独立交付一个别人能用的东西」。",
        "下一步四个方向：深 Web（Django REST / 前端）、深数据（pandas / numpy）、"
        "深自动化与爬虫、深测试与工程化。",
        "每个方向都是「先有项目、再学框架」，不要反过来先啃框架。",
    ],
    109: [
        "关卡 2 五条要闭卷自测：三个项目跑通、pytest 通过、接手陌生项目、说清扩展方向。",
        "★ 限时自测的价值在<b>暴露问题</b>——不测就永远不知道自己缺哪块。",
        "没过的项不要整体重学，只补那一项并重测。",
    ],
    110: [
        "★ 综合项目的四条统一要求：单文件 ≤300 行、pytest ≥8 条、README 说清怎么装怎么跑、"
        "推到公开仓库。",
        "做综合项目时把「先自己写 40 分钟，再看参考答案」的顺序守住——"
        "直接抄答案等于这 40 分钟白费。",
        "外星人入侵升级版要写 3 条 pytest 测试，覆盖纯逻辑函数而不是只测 UI。",
    ],
    111: [
        "★ 阶段 1 的函数、类、文件、异常、pytest，在三个项目里全都用上了——"
        "能讲清这条呼应关系，说明你是真的理解而不是背下来的。",
        "下一步方向要「先有项目、再学框架」，不要反过来先啃框架。",
        "阶段 2 的终点：能独立交付一个别人能用的东西，然后按兴趣选方向继续。",
    ],
}

# ── 讲评：检查本节实操写出来的代码 ──
REVIEWS = {
    65: {
        "items": [
            "三个库都装成功了吗？<code>pip list</code> 里能看到 pygame / matplotlib / plotly / requests 吗？",
            "建好项目目录了吗？是不是已经 <code>git init</code> 并 <code>.gitignore</code> 配好了？",
            "能说清阶段 2 和阶段 1 最大的不同吗（一句话就行）？",
        ],
        "summary": "阶段 1 学语法，阶段 2 学做项目——从今天起每节课都要问「这个文件在整个项目里的位置」。",
    },
    66: {
        "items": [
            "空窗口能弹出、能用 Q 退出吗？",
            "主循环的四步顺序你能不看代码背出来吗？",
            "把 <code>tick(60)</code> 删掉又加回来，各跑一次，说出差别。",
        ],
        "summary": "游戏是一个永不退出的循环，四步顺序错了就会抖、会卡、会关不掉。",
    },
    67: {
        "items": [
            "帧率锁死后，别人电脑上的速度和你的还一样吗？",
            "你能说清 KEYDOWN 和 QUIT 分别在什么情况下触发吗？",
            "背景色和窗口大小现在散落在几处？（超过一处就说明该收进 Settings）",
        ],
        "summary": "事件驱动 + 锁帧率，是实时程序能稳定跑在别人电脑上的两个前提。",
    },
    68: {
        "items": [
            "Settings 里的数值现在都集中在一处了吗？还有没有散落的魔法数字？",
            "<code>screen_rect</code> 的四个属性打印出来是多少？和你的窗口对得上吗？",
            "故意改错屏幕宽高，窗口变形了吗？",
        ],
        "summary": "把会变的数值收进一个类，是重构思维在真实项目里的第一次落地。",
    },
    69: {
        "items": [
            "按住右键，飞船是持续移动还是每按一次跳一格？",
            "故意删掉边界判断，看飞船飞出屏幕——然后把它加回来。",
            "飞船速度改成 3，手感变化明显吗？你能说出为什么边界判断要减半个飞船宽度吗？",
        ],
        "summary": "标志位 + screen_rect，是「持续移动 + 限制范围」的标准解法。",
    },
    70: {
        "items": [
            "主循环现在有几行？如果超过 10 行，重构还没到位。",
            "拆完之后行为完全一样吗？有没有顺手改坏的地方？",
            "六条常见错误你能现场复现几条？",
        ],
        "summary": "重构不是重写，是把长函数拆短、把重复合并——行为必须完全不变。",
    },
    71: {
        "items": [
            "你能用一句话说清 Group 和 list 的差别吗？",
            "★ 那个「漏删」bug 你亲手复现了吗？改对了吗？",
            "<code>groupcollide</code> 返回的列表里装的是什么？你打印过吗？",
        ],
        "summary": "遍历时删除会漏删——这条红线从阶段 1 一直跟到 Pygame。",
    },
    72: {
        "items": [
            "按住开火键不放，子弹数量稳住了吗？",
            "子弹飞出屏幕后会自动消失吗？你怎么知道它消失了？",
            "<code>limit</code> 去掉和保留，运行起来差别明显吗？",
        ],
        "summary": "限制子弹数量不是可有可无的优化——它是「按住不放会不会卡死」的保险。",
    },
    73: {
        "items": [
            "舰队能触边下移并反向吗？反向能恢复吗？",
            "★ 把速度改成 2，舰队还会不会飞出屏幕？你能解释为什么吗？",
            "把行数和列数各改一次，都能正常生成吗？",
        ],
        "summary": "整队移动靠一个方向标志位；边缘检测用 >= 而不是 ==，否则高速时会漏判。",
    },
    74: {
        "items": [
            "★ 把两个 True 改成 False，「外星人不消失」这个 bug 你复现了吗？",
            "撞到飞船时游戏会正确结束吗？余下飞船数对吗？",
            "外星人触底时会结束吗？",
        ],
        "summary": "碰撞检测有两个开关：kill_bullets 和 kill_aliens，设错就会出现「打不死」的鬼。",
    },
    75: {
        "items": [
            "★ 你用两个账号试过数据隔离吗？A 登录能看到 B 的笔记吗？",
            "<code>form.save(commit=False)</code> 少了中间补 owner 那步，数据归属会怎样？",
            "未登录直接访问需要登录的页面，会被踢到哪？",
        ],
        "summary": "数据隔离是 Web 开发最重要的安全红线——filter(owner=...) 不能写成 all()。",
    },
    76: {
        "items": [
            "点击 Play 能开始游戏吗？点它能重置吗？",
            "★ 文字能显示出来吗？中间经历了 font.render 这一步吗？",
            "游戏结束时鼠标指针隐藏了吗？",
        ],
        "summary": "Pygame 的文字必须先 render 成图像才能画——这是新手最常卡住的一步。",
    },
    77: {
        "items": [
            "分数是整数吗？带千分位逗号吗？",
            "去掉 <code>round(score, -1)</code> 看分数变成什么样？",
            "★ 最高分在重开游戏后保留了吗？如果没有，你打算怎么存？",
        ],
        "summary": "「数据与显示分离」是 UI 编程的通用套路；最高分要跨局保留，就该落到文件。",
    },
    78: {
        "items": [
            "难度会随击落外星人变高吗？还是会失控？",
            "重开一局，速度和分数倍率都复位了吗？",
            "余下飞船数用几个图标表示？减去一个了吗？",
        ],
        "summary": "动态难度靠 scale 统一管理；initialize 与 increase 的调用顺序不能反。",
    },
    79: {
        "items": [
            "第一张折线图跑出来了吗？标题和轴标签都加了吗？",
            "你能说出为什么推荐 <code>fig, ax = plt.subplots()</code> 吗？",
            "matplotlib 和 Plotly，你打算什么时候用哪个？",
        ],
        "summary": "静态图用 matplotlib，可交互图用 Plotly；多图时一定用面向对象的 fig, ax 写法。",
    },
    80: {
        "items": [
            "散点图上的点大小有差别吗？还是看起来一样大？",
            "点数从 1000 调到 10000，图还能接受吗？",
            "加 <code>random.seed()</code> 后两次运行结果一样吗？",
        ],
        "summary": "scatter 的 s / c / alpha 三件套，是把更多数据维度塞进一张图的手段。",
    },
    81: {
        "items": [
            "★ 不调 axis() 时点是不是贴边甚至被裁了？现在调了吗？",
            "颜色映射的颜色深浅能对应数值大小吗？",
            "保存出来的 PNG 标签全吗？<code>bbox_inches=\"tight\"</code> 去掉再存一次对比。",
        ],
        "summary": "axis() 留边距是 matplotlib 新手最高频的坑，看到点贴边第一反应就该是它。",
    },
    82: {
        "items": [
            "★ fill_walk 里的「拒绝原地不动」你写了吗？去掉会看到什么？",
            "5000 条路径画出来卡不卡？",
            "路径的起点和终点你高亮了吗？",
        ],
        "summary": "随机游走的灵魂在 fill_walk 的拒绝逻辑——不写它，路径就是一条直线。",
    },
    83: {
        "items": [
            "两个骰子的分布能看出差别吗？哪个更均匀？",
            "<code>results.count(value)</code> 统计对了吗？",
            "保存的 HTML 能点、能悬停吗？",
        ],
        "summary": "大数定律看着玄，实际掷一千次就懂了——可视化的价值就在这。",
    },
    84: {
        "items": [
            "★ 表头索引是用 enumerate 找的还是写死的？数据换一批还会对吗？",
            "日期字符串都转成 datetime 了吗？格式串和数据对得上吗？",
            "读之前确认过编码是 utf-8 了吗？",
        ],
        "summary": "真实数据的表头位置不固定——永远用 enumerate 找索引，不要硬编码列号。",
    },
    85: {
        "items": [
            "★ 缺失值那行你是跳过并打印警告了吗？还是静默跳过了？",
            "温度区间带画出来了吗？透明度和颜色协调吗？",
            "图上缺数据的地方看得出来吗？（看不出来说明处理得太隐蔽）",
        ],
        "summary": "处理缺失值可以，但必须打印警告——静默跳过会让你永远不知道少了多少数据。",
    },
    86: {
        "items": [
            "★ 经度和纬度的顺序对了吗？故意写反看图错在哪。",
            "点的大小随震级变化吗？颜色渐变合理吗？",
            "悬停文本能看到震级和位置吗？",
        ],
        "summary": "GeoJSON 里 coordinates[0] 是经度、[1] 是纬度——写反了图就画到地球另一边。",
    },
    87: {
        "items": [
            "★ <code>status_code</code> 检查了吗？404 的响应你没当成功用吧？",
            "<code>.json()</code> 拿到的字典，你打印过第一层和第二层的 key 吗？",
            "请求失败时程序是崩溃还是打印了提示？",
        ],
        "summary": "API 调用的三步：拿响应 → 查状态码 → 转字典，顺序错了后面全白搭。",
    },
    88: {
        "items": [
            "★ <code>X-RateLimit-Remaining</code> 你打印过吗？还剩几次？",
            "★ 如果写个循环拉 100 个仓库，会超限吗？你打算怎么处理？",
            "提取出来的 name / stars / url 三个字段都对吗？",
        ],
        "summary": "未认证每小时 60 次——写循环前先算一下会不会超限，超了要等重置。",
    },
    89: {
        "items": [
            "★ 图里的仓库名能点击跳转吗？这一步靠的是哪个参数？",
            "悬停时能看到 stars 和描述吗？",
            "条形图按 stars 排序了吗？不排序的话能一眼看出排名吗？",
        ],
        "summary": "Plotly 的可点击链接靠 customdata + hovertemplate 配合，不是设置一个 URL 属性那么简单。",
    },
    90: {
        "items": [
            "★ 某一条请求失败时，程序崩了还是跳过并计数？",
            "你有没有加限速？如果 50 条请求连着打，礼貌吗？",
            "两段式调用里，第一步拿到的 id 数量和第二步实际成功的数量一致吗？",
        ],
        "summary": "批量 API 调用的三条纪律：处理失败、限速、统计成功数——少一条就会在真实环境翻车。",
    },
    91: {
        "items": [
            "虚拟环境激活后命令行前面有 <code>(ll_env)</code> 吗？",
            "★ 关掉激活状态再 import django，会失败吗？（验证它真的隔离了）",
            "项目跑起来了吗？<code>runserver</code> 能打开首页吗？",
        ],
        "summary": "虚拟环境是每个项目的独立工具间——不激活就等于用全局环境，依赖会打架。",
    },
    92: {
        "items": [
            "★ 改完 models.py 跑 makemigrations 和 migrate 了吗？两步都跑了才生效。",
            "★ apps 加到 INSTALLED_APPS 了吗？没加的话模型根本不生效。",
            "进管理后台能看到 Topic 和 Entry 吗？",
        ],
        "summary": "改模型的三步曲：改代码 → makemigrations → migrate，少一步改动都不生效。",
    },
    93: {
        "items": [
            "★ 你能不看代码画出「URL → 视图 → 模板」的链路图吗？",
            "视图里三个 dict 传给模板，模板里用 {{ }} 取到了吗？",
            "故意把视图的 context 删掉，模板报什么错？读得懂吗？",
        ],
        "summary": "画得出请求链路图，就说明你懂 Django；画不出，说明只是抄了一遍代码。",
    },
    94: {
        "items": [
            "base.html 里的导航栏改动，所有页面都跟着变了吗？",
            "★ <code>{% url %}</code> 的名字写错时报 NoReverseMatch，你能看懂吗？",
            "访问一个不存在的 topic_id，是友好 404 还是丑陋的服务器错误？",
        ],
        "summary": "模板继承让「改一处全生效」；get_object_or_404 让错误页面友好——两个都要会。",
    },
    95: {
        "items": [
            "★ 删掉「补 owner」那一步，数据归属会变成什么样？你验证过吗？",
            "注册后是自动登录了吗？",
            "form 的 fields 白名单里有没有 owner？（有的话是安全隐患）",
        ],
        "summary": "数据归属三段式少一步，数据就不知道属于谁——这是 Web 开发的经典 bug。",
    },
    96: {
        "items": [
            "★ 你用两个账号实测过隔离吗？能截图说明吗？",
            "★ 把 filter 改成 all() 再改回来，你亲手试过吗？",
            "未登录访问受保护页面会被踢到哪？登录后能回到原来想去的页面吗？",
        ],
        "summary": "安全红线不能靠「我记得写了」——必须用两个账号实测。",
    },
    97: {
        "items": [
            "★ 用账号 A 去改账号 B 的条目，会被拒吗？你实测了吗？",
            "校验失败是跳转还是显示提示页？两种各有什么问题？",
            "新增条目的 owner 是不是当前用户？",
        ],
        "summary": "双重校验两层都要查；校验失败应跳转而非提示页——避免泄露资源是否存在。",
    },
    98: {
        "items": [
            "★ 装的是 django-bootstrap5 还是 bootstrap4？（第 3 版是前者）",
            "改 base.html 后所有页面都变了吗？",
            "表单现在还有没有一个一个手写的 input 标签？",
        ],
        "summary": "第 3 版用 django-bootstrap5；{% bootstrap_form %} 一行顶掉手写表单。",
    },
    99: {
        "items": [
            "★ requirements.txt 生成了吗？在 git 里吗？",
            "★ 云端靠它装依赖——它在吗？版本锁得住吗？",
            "你能在干净环境里按这个文件装一遍验证吗？",
        ],
        "summary": "requirements.txt 是云环境的采购清单——没有它，部署必失败。",
    },
    100: {
        "items": [
            "★ 两个 yaml 配置文件都写了吗？内容你读得懂吗？",
            "★ settings.py 里用 os.getenv 判断环境的分支，本地和「假装线上」各跑过吗？",
            "★ ALLOWED_HOSTS 改了吗？不改线上会怎样？",
        ],
        "summary": "本地/线上双环境靠环境变量判断；ALLOWED_HOSTS 是部署第一个必踩的坑。",
    },
    101: {
        "items": [
            "★ 上线检查清单逐条过了吗？DEBUG 关了吗？",
            "★ 访问不存在的 URL，看到的是定制错误页还是技术细节？",
            "线上出问题时，你知道怎么回滚吗？",
        ],
        "summary": "上线不是推上去就完了——检查清单走完、错误页定制好，才算真的部署。",
    },
    102: {
        "items": [
            "你能画一张三个项目的技术地图吗？每块解决了什么问题？",
            "★ 你的三个项目各走了七步流程里的哪几步？README 写了吗？",
            "三个项目推到公开仓库了吗？",
        ],
        "summary": "阶段 2 的产出不是「跑通了」，是「按工程流程跑通了并留下痕迹」。",
    },
    103: {
        "items": [
            "★ 你的项目里有超过 300 行的文件吗？该拆吗？",
            "★ 仓库里有密钥吗？用 .gitignore 挡了吗？（提交过就必须去平台改密钥）",
            "★ 你能读懂一个没写过的 500 行项目的结构吗？",
        ],
        "summary": "单文件不超 300 行、密钥不进 git、能读懂别人的代码——这三条决定你是谁。",
    },
    104: {
        "items": [
            "★ 关卡 2 五条，你过了几条？没过的定补齐计划了吗？",
            "「学习笔记」公网能访问吗？让别人试过吗？",
            "★ 你能用一句话说清每个项目「还能怎么扩展」吗？",
        ],
        "summary": "关卡 2 考的不是记住多少 API，是「能不能独立把一个东西做出来并交出去」。",
    },
    105: {
        "items": [
            "你的综合项目能给别人看吗？README 写清怎么装怎么跑了吗？",
            "★ 阶段 1 的学习总结写了吗？最大的收获是什么？",
            "四个下一步方向里，你选了哪个？为什么？",
        ],
        "summary": "阶段 2 的终点是「能独立交付一个项目」，然后按兴趣选方向继续。",
    },
    106: {
        "items": [
            "★ 上线检查清单逐条过了吗？DEBUG 关了吗？ALLOWED_HOSTS 改了吗？",
            "★ 访问不存在的 URL，看到的是定制错误页还是技术细节？",
            "线上出问题时你知道怎么回滚吗？还是只能在线上硬改？",
        ],
        "summary": "上线不是推上去就完了——清单走完、错误页定制好，才算真的部署。",
    },
    107: {
        "items": [
            "★ 关卡 2 五条，你过了几条？没过的定补齐计划了吗？",
            "「学习笔记」公网能访问吗？你让别人试过吗？",
            "★ 你能用一句话说清每个项目「还能怎么扩展」吗？",
        ],
        "summary": "关卡 2 考的不是记住多少 API，是「能不能独立把东西做出来并交出去」。",
    },
    108: {
        "items": [
            "三个项目的 README 都写清「怎么装、怎么跑」了吗？",
            "★ requirements.txt 和 .gitignore 都进仓库了吗？",
            "★ 你的仓库里有超过 300 行的文件吗？该拆吗？",
        ],
        "summary": "工程件的齐全程度，决定别人能不能用你的项目——也是关卡 2 的硬指标。",
    },
    109: {
        "items": [
            "★ 关卡 2 五项逐条自测打勾了吗？没过的项定补齐计划了吗？",
            "限时自测暴露出来的问题，是知识点不会还是流程没走？",
        ],
        "summary": "限时自测的价值在于暴露问题——不测就永远不知道自己缺哪块。",
    },
    110: {
        "items": [
            "综合项目开工了吗？A / B / C 选的是哪个，为什么选它？",
            "统一要求四条做到位了吗？",
        ],
        "summary": "综合项目是阶段 2 的收尾产出——做完它，你才真的「独立做过一个项目」。",
    },
    111: {
        "items": [
            "★ 阶段 1 的学习总结写了吗？最大的收获是什么？",
            "四个下一步方向里你选了哪个？说得出理由吗？",
            "★ 你能说清「为什么阶段 1 的函数/类在阶段 2 全都用上了」吗？",
        ],
        "summary": "阶段 2 的终点是「能独立交付一个项目」，然后按兴趣选方向继续。",
    },
}