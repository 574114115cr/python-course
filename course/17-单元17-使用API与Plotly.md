# 单元 17：使用 API 与 Plotly

> 对应教材第 17 章「使用 API」
> 阶段 2 · 项目 2：数据可视化
> 本单元目标：**学会向互联网上的数据接口（API）要数据，用 Plotly 把 GitHub 最热门的 Python 仓库和 Hacker News 热帖画成可交互图表**

---

## 一、学习目标

完成本单元后，你应该能够：

1. 用一句话说清 API 是什么，说得出「餐厅服务员」这个类比里调用方和服务端各自的职责。
2. 用 `requests.get(url, headers=..., timeout=...)` 发出请求，读懂**响应对象**上的 `status_code`、`text`、`headers`、`json()`。
3. 根据 `status_code` 判断成败：说清 200 / 403 / 404 / 429 / 500 各自意味着什么，写出「检查状态码 + `try/except`」的固定套路。
4. 调用 GitHub search API（带 `Accept: application/vnd.github+json` 头），从 `response_dict["items"]` 里提取 `name`、`stargazers_count`、`html_url`、`description`、`owner.login`。
5. 用 `response.headers["X-RateLimit-Remaining"]` 查剩余配额，说清「未认证每小时 60 次」，知道超限返回 403。
6. 用 `px.bar`、`hover_data`、`color_discrete_map` 定制条形图，并用 `custom_data` + `hovertemplate` 做出**可单击的链接**。
7. 走通 Hacker News 的「两段式调用」：先取 `topstories.json` 拿 id 列表，再对每个 id 取 `item/{id}.json` 拿详情。

---

## 二、核心知识点讲解

### 2.1 API 是什么：餐厅服务员的类比

上一单元数据是**下载文件**得到的。这一单元换个思路——**不下载文件，直接对着服务方要数据**，这个「服务方」就是 API。

先捋一遍教材 17.1 的背景：**Git** 是给代码拍快照的版本控制系统；**GitHub** 是托管 Git 仓库的网站；一个项目文件夹叫**仓库**（repo）；别人给你项目点的赞叫**星标**（star），star 数是「热门程度」的粗略度量。而 **API** 就是 GitHub 提供的「服务员」——你报菜名，它端出 JSON。

**API（Application Programming Interface，应用程序编程接口）** 是一种约定：服务方公开一组「网址 + 参数 + 返回格式」，你按约定发请求，它按约定回数据，**你不必知道它怎么实现**。

★ 生活化类比：**餐厅服务员**。

```text
你（调用方）                服务员（API）              厨房（服务器）
   │ 念菜名 ──────────────────▶  │  走进厨房、和厨师商量、   │
   │ "我要宫保鸡丁"（= URL+参数）  │                        │
   │  ◀────────────────────────── │                        │
   │  一盘菜，或一句"卖完了"       │                        │
   ▼
吃（= 你处理返回的数据）
```

这个类比精确在三处：**① 你不需要进厨房**，也不必知道宫保鸡丁先爆香还是先下肉——**服务方可以随时换做法，只要端出来的还是那道菜**，这就是「接口稳定、实现可变」；**② 菜单公开、厨房私密**——文档告诉你能点什么，服务器代码不必看；**③ 服务员会拒绝你**——「今天卖完了」「菜不在菜单上」对应程序里的 **403 / 404**，★ **要有被拒绝的心理准备**。

本单元只碰教材涉及的三个接口：**GitHub search API**（返回仓库搜索结果）、**Hacker News API**（返回 id 列表与帖子详情）、以及单元 16 用过的 **USGS 地震 GeoJSON**。

```bash
pip install requests plotly          # requests 是本单元新面孔
```

**先建立一件容易被忽略的事**：`response.text` 是**字符串**，不是字典。字符串上取 `["total_count"]` 不会返回 `None`，而是直接抛 `TypeError`——`.json()` 那一步就是把字符串编译成数据结构的过程，它不是一个可省的「顺手调用」：

```python
# 响应体的两种形态：字符串与字典，差一次 json.loads
import json

RAW = '{"total_count": 4350000, "items": [{"name": "django"}]}'

print("response.text 的类型：", type(RAW).__name__)
print("  直接取字段：", end=" ")
try:
    RAW["total_count"]
except TypeError as error:
    print(f"{type(error).__name__}: {error}")

data = json.loads(RAW)                  # 等价于 response.json()
print("\nresponse.json() 之后：", type(data).__name__, "，键：", list(data))
print("  取字段：", data["total_count"], data["items"][0]["name"])
print("  取不存在的键：", end=" ")
try:
    data["message"]
except KeyError as error:
    print(f"KeyError: {error}  <- 403 时往往只有 message，没有 items")
```

### 2.2 requests.get() 与响应对象：先看 status_code ★

`requests` 是 Python 里发 HTTP 请求最常用的第三方库（单元 9 讲过「标准库不够用就装第三方库」）。核心只有一个函数 `requests.get(url)`，它返回一个 **`Response` 响应对象**——像**快递包裹**：拆之前先看面单（`status_code`）确认送对了没，再拆箱取货。对象上有四个你会反复用的东西：`status_code`（int，状态码，**判断成败的第一道关卡**）、`text`（str，响应体原始字符串）、`headers`（字典，大小写不敏感，能看到剩余配额）、`json()`（方法，把 JSON 响应体转成 Python 字典）。

**status_code 必须先看**，200 和 403 后面接的操作完全不同：

| 状态码 | 含义 | 你该做什么 |
|---|---|---|
| 200 | 成功 OK | 放心用 `response.json()` |
| 403 | 禁止 Forbidden | 多半是**速率限制超了**或需要认证，别死循环重试 |
| 404 | 没找到 | 网址或资源 ID 写错了 |
| 429 / 500 | 请求过多 / 服务器出错 | 等一会儿再来，别重试轰炸 |

★ 关键：**不要先写 `response.json()` 再想成功失败。** 403 时响应体**也是合法 JSON**（GitHub 返回一段解释原因的 JSON），`.json()` 照样成功——但内容是错误信息。**顺序：先 `status_code`，再 `.json()`。**

取数函数三个要点一个都不能省：**① `try/except` 包住 `requests.get()`**——网络请求永远可能失败；**② 检查 `status_code`**；**③ 失败要打印，不要静默跳过**——静默跳过会画出「少了 30 个仓库」的图，你还以为它成功了。**失败的请求要留下痕迹。**（完整可运行版本见示例 3 的 `get_json`。）

上面那张表可以直接写成一张「状态码 → 下一步」的翻译表，比散落的 `if` 更好维护：

```python
# 先 status_code 再 .json()：一张决策表写成函数
NEXT_STEP = {
    200: "成功：放心调用 response.json()",
    403: "被拒绝：多半是配额超了，打印剩余配额后停下，别死循环重试",
    404: "网址或资源 ID 写错了：核对 URL 和参数",
    429: "请求太多：等一会儿再来（读 Retry-After 头）",
    500: "服务器自己出错：稍后重试，别改自己的代码",
}


def handle(status_code, remaining=None):
    """返回「下一步该做什么」。任何未知状态码都不许当成功。"""
    step = NEXT_STEP.get(status_code)
    if step is None:
        step = f"没见过的状态码 {status_code}：打印 response.text 前 200 字再判断"
    return step


for code in [200, 403, 404, 429, 500, 418]:
    print(f"{code}: {handle(code)}")
print("\n★ 顺序纪律：if response.status_code != 200: 打印并 return None")
print("   然后才是 response.json() —— 反过来写，403 的错误 JSON 会被当成数据。")
```

### 2.3 .json()：把响应体变成字典 ★

这是 API 调用**最关键的一步**：把 JSON 文本解析成 Python 的字典和列表，从此你就能用单元 5 的字典取值、单元 7 的函数来处理它。下面这份「已经拿在手上」的响应字典（真实项目里来自 `response.json()`）长这样：

```text
response_dict（字典）
├── total_count: 4350000         ← 总命中数，不是结果条数！
├── incomplete_results: False
└── items: [ ... ]               ← ★ 真正的结果在这里，是个列表
    ├── [0]  ← 每个元素又是一个字典（一个仓库）
    │   ├── name / stargazers_count / html_url / description
    │   │                              ↑ ★ 这个字段可能是 None！
    │   └── owner: { "login": "vinta" }  ← 字典套字典
    ├── [1] ...
    └── [N] ...
```

取值路线就是**一层层剥**：`response_dict["items"][0]["owner"]["login"]` → `vinta`。★ 难在**嵌套的方括号**，四对括号很容易写错。**技巧：拆成中间变量**一层层剥。

```python
# 四对括号怎么剥：拆成中间变量，一层层取
payload = {
    "total_count": 2,
    "items": [
        {"name": "django", "stargazers_count": 78000,
         "owner": {"login": "django"}, "html_url": "https://github.com/django/django"},
        {"name": "flask", "stargazers_count": 67000,
         "owner": {"login": "pallets"}},          # ★ 故意缺 html_url
    ],
}

items = payload["items"]                          # ① 先拿列表
first = items[0]                                  # ② 再拿第一个仓库
owner = first["owner"]                            # ③ 再进 owner
print("一行版：", payload["items"][0]["owner"]["login"])
print("拆开写：", owner["login"])

print("\nfor 循环里剥（真实代码几乎都长这样）：")
for index, repo in enumerate(items, 1):
    login = repo["owner"]["login"]                # 字典套字典
    url = repo.get("html_url", "（没有链接）")     # 可选字段用 .get
    print(f"  {index}. {repo['name']:<8}{repo['stargazers_count']:>7,}  "
          f"by {login:<8}{url}")

print("\n★ 核心结构用 []，可选字段用 .get()：")
try:
    payload["message"]
except KeyError as error:
    print(f"  payload['message'] -> KeyError: {error}（说明 API 变了或返回错误）")
print("  payload.get('message', '（没有这个键）') ->",
      payload.get("message", "（没有这个键）"))
```

### 2.4 GitHub search API：请求头与速率限制 ★

教材 17.1 的实操目标是「概述最受欢迎的仓库」，用的接口是 GitHub search API。这个网址要用问号把「接口地址」和「参数」分开读：

```text
https://api.github.com/search/repositories   ← 接口路径：搜索仓库
?q=language:python                           ← q（query）：用 Python 写的仓库
&sort=stars                                  ← sort：按 star 数排序（最热在前）
&per_page=10                                 ← 每页 10 条（可选，默认 30）
```

**请求头（headers）是 API 的另一半。** 教材这一步要求带上 `headers = {"Accept": "application/vnd.github+json"}`。头干什么用？类比**点菜时的备注栏**：「我要微辣、多加葱」——不改你要的菜，而是告诉厨房**要什么格式**。

头就是一个普通字典，所以可以「拼」：再加认证 token 时用 `|` 合并两本字典即可。查的时候注意 **HTTP 头名大小写不敏感**，自己比对时先统一 `lower()`：

```python
# 请求头是个字典：用 | 合并，键名大小写不敏感
ACCEPT_JSON = {"Accept": "application/vnd.github+json"}
AUTH = {"authorization": "Bearer ghp_xxxx"}        # 小写也能被认出来

headers = ACCEPT_JSON | AUTH                        # Python 3.9+ 的字典合并
print("合并后：", headers)

# HTTP 头名大小写不敏感：查的时候统一 lower() 再比
lookup = {key.lower(): value for key, value in headers.items()}
for name in ["Accept", "ACCEPT", "authorization"]:
    print(f"  查 {name:<14}-> {lookup.get(name.lower(), '（没有）')}")

print("\n三个必须带的头 / 参数：")
print("  Accept: application/vnd.github+json   # 要 JSON 格式")
print("  timeout=10                            # 不设就会永远挂着")
print("  params={'q': 'language:python'}       # 让 requests 帮你拼 & 和编码")
```

有了字典，接下来就是**提取成几个平行的列表**（Plotly 画图要的就是平行列表，单元 16 画地震图时你已经用过这套路）：`repo_names` 装 `name` 当柱子标签、`stars` 装 `stargazers_count` 当柱子高度、`repo_urls` 装 `html_url` 做可点击链接、`descriptions` 装 `description`、`owners` 装 `owner.login` 上色。完整循环见示例 2。

★ 提取时的三个坑：**① `items` 和 `total_count` 不是一回事**——后者是「符合条件的有几百万个」，前者才是**这一次实际返回给你的**（默认 30 条，可加 `&per_page=100`）；**② `description` 可能是 `None`**，写 `repo["description"] or "（没写简介）"`；**③ 用 `.get()` 防缺字段**——`.get("forks_count", 0)` 拿不到就返回默认值，但 `response_dict["items"]` 这种「核心结构」就该用 `[]`，缺了说明 API 变了。

**速率限制。** 任何正经 API 都有速率限制——服务器资源有限，人人每秒请求 1000 次网站就垮了。GitHub 的规矩：**未认证每小时 60 次**，登录后（带 token）5000 次。**超限返回 403 Forbidden**，同时响应头 `X-RateLimit-Remaining` 告诉你还剩几次、`X-RateLimit-Limit` 告诉你总配额。完整守门员代码见示例 3。

★ **新手最容易忽略的一点：配额按「一小时窗口」算，不是「每 60 次后立刻重置」。** 刚发出 3 次请求后 `X-RateLimit-Remaining` 应该显示 57 而不是 60。要连续取几十条数据时**主动 `time.sleep(1)` 放慢速度**。

想多拿几条就得翻页，而翻页的参数是算出来的，不是猜出来的：

```python
# 分页：页码怎么算、什么时候该停
def page_params(page, per_page=10, query="language:python"):
    """把「第几页、每页几条」翻译成 API 认识的参数。"""
    return {"q": query, "sort": "stars", "per_page": per_page, "page": page}


def total_pages(total_count, per_page=10):
    """总命中数 -> 总页数；除不尽要向上取整。"""
    return -(-total_count // per_page)          # 整数向上取整的惯用写法


print("第 1~3 页的参数：")
for page in (1, 2, 3):
    print(" ", page_params(page))

print("\n总命中数 23 条、每页 10 条 ->", total_pages(23), "页")
print("总命中数 20 条、每页 10 条 ->", total_pages(20), "页（整除时不要多算一页）")

print("\n★ 三个坑：")
print("  1. total_count 是几百万，不是你这次拿到的条数；别照着它翻几千页")
print("  2. 每页上限 100；再大也没用，API 会默默截断")
print("  3. 翻页要 sleep(1)，否则几十页就把 60 次配额打光")
```

**四条必须养成的工程习惯**（教材 17.1 反复强调的）：请求包 `try/except`（否则断网就崩）、检查 `status_code`（否则把 403 的错误 JSON 当数据用）、失败请求打印出来（否则数据悄悄少一半你却以为完整）、注意限速主动 sleep（否则被拒甚至被封禁）。

还有一个特别值得学的做法：**把拿到的数据存下来**（教材存成 `github_repos.json`，见示例 3）。API 数据随时会变，调图时反复请求既慢又烧配额；有了缓存，画图代码就**完全不依赖网络**。

### 2.5 Plotly 可视化仓库：悬停提示与颜色

数据齐了，进入 17.2。上一单元你用过 `px.scatter_geo`，这里换 `px.bar`——横向柱子，标签文字长也不怕挤在一起。三个最常用定制参数：`hover_name`（悬停时**加粗显示的主标题**，这里是仓库名）、`hover_data`（额外的悬停信息）、`color` + `color_discrete_map`（让某个字段的不同取值分到不同颜色，并用「取值 → 颜色」的字典**固定配色**，保证每次生成的图风格一致）。用 `owner` 分组上色，一眼就能看出哪几个仓库是同一个作者的。

> ★ **补充说明（教材未涉及，plotly 7.x 的变化）**：`hover_data` 和 `custom_data` 传**列名字符串**时必须有 DataFrame 兜底，否则报 `ValueError: String or int arguments are only possible when a DataFrame ... is provided`。所以先把平行列表装进 `pd.DataFrame({...})`（键是列名），再 `px.bar(df, x="name", ...)`。样式参数见示例 4 的注释。

### 2.6 ★ 可单击链接：custom_data 与 hovertemplate

这是 17.2 最有价值、也最容易卡住的一节。目标：悬停在某根柱子上时，除了名字和 star 数，还显示一行**可以点击的链接**，点一下跳到那个仓库的网页。

**问题在哪？** Plotly 默认只把数据**当纯文本**显示。URL 看着像网址，但**点不动**。解法两步：`custom_data=["html_url"]` 把 URL 挂到每根柱子的「自定义数据」上 → `hovertemplate` 里插一个 `<a href='%{customdata[0]}'>Open in GitHub</a>` 链接（可运行版见本节末，完整版见示例 4）。

★ **索引别搞混，这是本节 90% 的错误来源：** `%{hovertext}` 是 `hover_name` 的内容，`%{y}` 是 y 轴数值（`:,` 是千分位格式），`%{customdata[n]` 是 `custom_data` 里的第 n 列，`<extra></extra>` 清空右上角默认显示的 `trace 0` 之类字样。**写之前先把列和索引一一对齐**；不确定就先 `print([list(r) for r in fig.data[0].customdata])` 看每一列到底是什么。

不开浏览器也能做这个「对齐」检查——`customdata` 就是个二维列表，把模板里的占位符替换一遍，看看填出来的是什么：

```python
# hovertemplate 的索引自检：customdata 到底装了几列
custom_data = [
    ["https://github.com/vinta/awesome-python", "vinta"],
    ["https://github.com/django/django", "django"],
    ["https://github.com/pallets/flask", "pallets"],
]
TEMPLATE = ("<b>%{hovertext}</b><br>"
            "作者：%{customdata[1]}<br>"
            "<a href='%{customdata[0]}'>Open in GitHub</a><extra></extra>")

print("每根柱子的 customdata：")
for index, row in enumerate(custom_data):
    print(f"  第 {index} 根：{row}")
print("  每行列数：", len(custom_data[0]), "-> 索引只能是 0 和 1")

print("\n模拟 Plotly 填模板（柱子 1）：")
filled = (TEMPLATE.replace("%{hovertext}", "django")
                  .replace("%{customdata[1]}", custom_data[1][1])
                  .replace("%{customdata[0]}", custom_data[1][0])
                  .replace("<extra></extra>", ""))
print("  ", filled)

print("\n★ 先对齐再写模板，别凭记忆数下标：")
print("   custom_data=['html_url']               -> 只有 [0]")
print("   custom_data=['html_url', 'owner']      -> [0] 是链接、[1] 是作者")
```

**为什么链接文字是写死的？** HTML 的 `<a href='地址'>显示文字</a>` 里地址和文字是两个独立部分。教材把 `html_url` 在 `custom_data` 里放两遍分别填这两处，但新版 plotly 不允许重复列名（报 `DuplicateError`）；本讲义**只传一列填 `href`，文字写死成 "Open in GitHub"**——效果一样，代码更短。

**链接点了没反应？三个必查项：** ① `custom_data` 的**列名写错了**（写 `url` 但 DataFrame 里是 `html_url`）——Plotly **静默忽略**不存在的列，链接变空白；② 忘了 `<extra></extra>` 或忘了 `write_html` 保存；③ 导出的不是 HTML（比如 png）——**链接是 HTML 的能力，静态图片不可能有。**

可运行版本见示例 4（数据更完整，还加了配色）。

### 2.7 Hacker News API：先拿列表、再取详情的两段式调用

17.3 换个数据源、换一种调用模式。Hacker News 是程序员社区（https://news.ycombinator.com ），它的 API 极其简洁：

```text
https://hacker-news.firebaseio.com/v0/topstories.json     ← 热门文章 id 列表
https://hacker-news.firebaseio.com/v0/item/{id}.json      ← 单篇文章的详情
```

★ **为什么分两次？** 这就是**两段式调用模式**，理解它比记住网址重要得多。第一段 `topstories.json` 返回的是一串**数字**——只知道编号，还没有任何内容：

```json
[38491822, 38491760, 38491576, 38491485, 38491381]
```

第二段才对每个 id 请求 `item/{id}.json`，拿回下面这样的条目：

```json
{
  "by": "dhouston",
  "descendants": 71,
  "id": 38491381,
  "score": 216,
  "title": "The Hammerspace Interaction",
  "type": "story",
  "url": "https://www.youtube.com/watch?v=Ha8bB5gHYSc"
}
```

**为什么这么设计？** 因为它**通用又省流量**：一份 id 列表能配不同详情查询，组合出「当前最热」「某作者的帖子」等成百上千种需求。类比**报纸的目录页只印标题和页码**。`title` 是主标题，`score`（得分 ≈ 点赞数）当热度，`descendants` 是评论条数。

★ 两个坑：**① `"by"` 是合法 JSON 键，但不能当 Python 变量名**——`by = item["by"]` 会**语法错误**（`by` 是 Python 关键字），所以老老实实 `item["by"]` 直接取值；**② `url` 可能是 `null`**（Ask HN 帖没有外链）。

这两处兜底不用等真接口，把「一条详情」写成函数就能测：

```python
# 第二段取详情：null 条目要跳过，url 为空要兜底
SAMPLE = {
    101: {"title": "Why SQLite", "score": 142, "url": "https://sqlite.org/why.html"},
    102: {"title": "Ask HN: 你怎么记笔记", "score": 88, "url": None},   # ★ 没有外链
    103: None,                                                          # ★ 已被删除
}


def get_item(story_id):
    """真项目里是 requests.get(item_url)，这里用字典冒充。"""
    return SAMPLE.get(story_id)


def to_row(story_id):
    item = get_item(story_id)
    if not isinstance(item, dict):            # None = 删除；非字典 = 意外
        return None
    return {
        "title": item.get("title") or "(无标题)",
        "score": item.get("score", 0),
        "link": item.get("url")
                or f"https://news.ycombinator.com/item?id={story_id}",
    }


for story_id in (101, 102, 103, 999):
    row = to_row(story_id)
    print(f"{story_id}: {'跳过（条目已删除或请求失败）' if row is None else row}")

print("\n★ 两处兜底都是为了「每根柱子都有链接」：")
print("  item is None      -> continue，别让 item['title'] 抛 TypeError")
print("  url is None       -> 退回讨论页，链接不会变成空白")
```

完整写法见示例 5，三个细节：**① `story_ids[:5]`**——列表有 500 个 id，你只想画 5 根柱子，**先切片再请求**省配额；**② `item_dict is None` 的检查**——对删掉的条目 API 返回 `null`，不检查的话 `item_dict["title"]` 抛 `TypeError`；**③ `url` 的兜底**——用 `https://news.ycombinator.com/item?id={story_id}` 顶上。★ 这就是 2.6「可点击链接」技术在真实场景里的意义：**链接可能是空的，你得给它一条退路。**

---

## 三、可运行代码示例

> 所有示例都**自带离线兜底**：网络正常时打真实 API，网络不通时用内置样例继续跑完。
> 输出文件生成在当前目录，演示完可以删掉。

### 示例 1：认识 API 网址的结构 + 第一次调用

```python
# api_basics.py —— 先看清网址结构，再发一个真实请求（离线有兜底）
import requests

GITHUB_SEARCH = "https://api.github.com/search/repositories?q=language:python&sort=stars"
print("--- 网址里的参数 ---")
for pair in GITHUB_SEARCH.split("?", 1)[1].split("&"):
    key, _, value = pair.partition("=")
    print(f"  {key:10} = {value}")

# ===== 发一个真实请求；离线兜底数据结构和真实响应一致 =====
FALLBACK = {"total_count": 4350000, "incomplete_results": False,
            "items": [{"name": "awesome-python", "stargazers_count": 220000,
                       "owner": {"login": "vinta"}, "description": "A list",
                       "html_url": "https://github.com/vinta/awesome-python"}]}

try:
    response = requests.get(GITHUB_SEARCH + "&per_page=3",
                            headers={"Accept": "application/vnd.github+json"},
                            timeout=10)
except requests.exceptions.RequestException as error:
    print("网络请求失败：", error)
    response_dict = FALLBACK
else:
    print("状态码：", response.status_code,
          "剩余配额：", response.headers.get("X-RateLimit-Remaining", "不适用"))
    if response.status_code != 200:
        print("响应片段：", response.text[:200])      # 失败也要打印，别静默跳过
        response_dict = FALLBACK
    else:
        response_dict = response.json()

print("\ntotal_count:", response_dict["total_count"],
      "本次返回 items:", len(response_dict["items"]))
print("items[0] 的键:", list(response_dict["items"][0].keys()))
```

### 示例 2：处理响应字典——提取平行列表

```python
# parse_response.py —— 把响应字典变成 Plotly 需要的平行列表（完全离线）
RAW = [("awesome-python", 220000, "vinta", "A list of awesome-python"),
       ("free-python-games", 95000, "tasnowak", None),      # ★ 故意留空，测兜底
       ("django", 78000, "django", "The web framework")]
items = [{"name": n, "stargazers_count": s, "owner": {"login": o},
          "description": d, "html_url": f"https://github.com/{o}/{n}"}
         for n, s, o, d in RAW]

repo_names, stars, repo_urls, descriptions, owners = [], [], [], [], []
for repo_dict in items:
    repo_names.append(repo_dict["name"])
    stars.append(repo_dict["stargazers_count"])
    repo_urls.append(repo_dict["html_url"])
    descriptions.append(repo_dict["description"] or "（作者很懒，没写简介）")
    owners.append(repo_dict["owner"]["login"])

print("--- 提取结果 ---")
for name, star_count, owner in zip(repo_names, stars, owners):
    print(f"{name:<20}{star_count:>9,}  by {owner}")

# .get() 演示「字段可能不存在」
print("\nforks_count 用 .get 取默认值：", items[0].get("forks_count", 0))

# 按 star 从多到少排序；再断言五个列表等长，否则画图一定出错
for i in sorted(range(len(stars)), key=lambda i: stars[i], reverse=True):
    print(f"{repo_names[i]:<20}{stars[i]:>9,}")
assert len(repo_names) == len(stars) == len(repo_urls) == len(descriptions) == len(owners)
print("五个列表等长：True（共", len(repo_names), "条）")
```

### 示例 3：速率限制守门员 + 缓存响应

```python
# rate_limit_guard.py —— 看配额 + 缓存；需要网络，没网走 except 分支
import json
import time
from pathlib import Path

import requests

URL = "https://api.github.com/search/repositories"
HEADERS = {"Accept": "application/vnd.github+json"}
CACHE = Path("github_repos.json")   # 跑完会删掉


def get_json(url, headers=None):
    """try/except + 状态码检查，失败返回 None——本单元的通用取数套路。"""
    try:
        response = requests.get(url, headers=headers or {}, timeout=10)
    except requests.exceptions.RequestException as error:
        print(f"  请求失败：{error}")        # 网络断了、DNS 失败、超时……
        return None
    if response.status_code != 200:
        # 403/404/429/500 一律先打印出来，别静默跳过
        print(f"  状态码 {response.status_code}，剩余配额 "
              f"{response.headers.get('X-RateLimit-Remaining', '未知')}")
        return None
    # ★ 配额只在响应对象上有，顺便查一下，低于 5 就收手
    remaining = response.headers.get("X-RateLimit-Remaining")
    if remaining is not None and int(remaining) < 5:
        print(f"  警告：配额只剩 {remaining}")
    return response.json()


for query in ["language:python", "language:javascript"]:
    time.sleep(1)              # 主动限速，别把人家服务器打爆
    data = get_json(f"{URL}?q={query}&sort=stars&per_page=3", HEADERS)
    if data is None:
        break                  # 网络断了就别试下一轮
    print(f"[{query}] 拿回", [item["name"] for item in data["items"]])
    CACHE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    break

print("已缓存到", CACHE, "，下次调试直接读它，不用再请求网络")
CACHE.unlink(missing_ok=True)     # 清理；真做项目时把缓存留着
print("说明：未认证每小时 60 次；403 和 429 都可能是限流信号。")
```

### 示例 4：Plotly 条形图——悬停提示、颜色、可点击链接

```python
# bar_chart.py —— 悬停提示 + 固定配色 + 可点击链接
# 跑完生成 bar_chart.html，用浏览器打开悬停并点击；看完可以删掉
import pandas as pd
import plotly.express as px

# 把平行列表装进 DataFrame，px 的列名写法（custom_data=["url"]）才可用
NAMES = ["awesome-python", "django", "flask"]
OWNERS = ["vinta", "django", "pallets"]
df = pd.DataFrame({"name": NAMES, "stars": [220000, 78000, 67000],
                   "description": ["Python 资源大全", "重量级 Web 框架", "轻量级 Web 框架"],
                   "owner": OWNERS,
                   "html_url": [f"https://github.com/{o}/{n}"
                                for o, n in zip(OWNERS, NAMES)]})

fig = px.bar(
    df, x="name", y="stars",
    hover_name="name",                            # 加粗主标题
    hover_data=["description", "owner"],          # 额外悬停信息
    custom_data=["html_url"],                     # ★ 把 URL 挂到柱子上
    color="owner",                                # 按作者分组上色
    color_discrete_map={"vinta": "seagreen", "django": "green",
                        "pallets": "darkorange"},  # 固定配色，风格稳定
    text_auto=".2s",                                # 柱子上标数值（219k 这种）
    title="Most-Starred Python Repositories",
)
fig.update_traces(
    marker_line_width=1.5, marker_line_color="gray",    # 柱子描边
    opacity=0.9,
    hovertemplate="<b>%{hovertext}</b><br>Stars: %{y:,}<br>"
                   "<a href='%{customdata[0]}'>Open in GitHub</a><extra></extra>",
)
fig.update_layout(
    title={"text": "Most-Starred Python Repositories", "x": 0.5, "xanchor": "center",
           "font": {"size": 20}},
    xaxis_title=None, yaxis_title="Stars")
fig.write_html("bar_chart.html")
print("已生成 bar_chart.html —— 悬停柱子，点 Open in GitHub 试试")

for trace in fig.data:      # 验证 customdata 到底装了什么
    print("柱子", list(trace.x), "的 customdata:", [list(r) for r in trace.customdata])
```

### 示例 5：Hacker News 两段式调用

```python
# hacker_news.py —— 先列表、再详情，限速 + 失败处理
# 没网时自动改用内置样例，保证程序跑完；跑完的 hn_top.html 可以删掉
import time

import pandas as pd
import plotly.express as px
import requests

TOP_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{id}.json"
TOP_N = 5
FALLBACK = {38491381: {"title": "Hammerspace Interaction", "score": 216},
            38491760: {"title": "Ask HN", "score": 158,
                       "url": None},                   # ★ 没外链，测兜底
            38491822: {"title": "Why SQLite", "score": 142}}


def get_json(url):
    """try/except + 状态码检查，失败返回 None。"""
    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.RequestException as error:
        print(f"  请求失败：{type(error).__name__}")
        return None
    if response.status_code != 200:
        print(f"  状态码 {response.status_code}，跳过")
        return None
    return response.json()


# ===== 第一段：拿 id 列表；拿不到就用内置样例 =====
story_ids = get_json(TOP_URL) or list(FALLBACK)
print(f"第一段：{len(story_ids)} 个 id，只取前 {TOP_N} 条")

# ===== 第二段：逐个 id 取详情 =====
titles, scores, links = [], [], []
for index, story_id in enumerate(story_ids[:TOP_N]):
    if index > 0:
        time.sleep(1)                  # 主动限速
    item_dict = get_json(ITEM_URL.format(id=story_id)) or FALLBACK.get(story_id)
    if not item_dict:
        print(f"  跳过 id {story_id}")
        continue
    titles.append(item_dict.get("title") or "(无标题)")
    scores.append(item_dict.get("score", 0))
    # ★ url 可能是 None，兜底成讨论页，保证每根柱子都有链接
    links.append(item_dict.get("url")
                 or f"https://news.ycombinator.com/item?id={story_id}")
    print(f"  {titles[-1]:<45}{scores[-1]:>5}")

# ===== 画图 =====
if titles:
    df = pd.DataFrame({"title": titles, "score": scores, "link": links})
    fig = px.bar(df, x="title", y="score", hover_name="title",
                 custom_data=["link"], title="Top HN Stories")
    fig.update_traces(hovertemplate="<b>%{hovertext}</b><br>Score: %{y:,}<br>"
                     "<a href='%{customdata[0]}'>Read</a><extra></extra>")
    fig.update_layout(xaxis_title=None, yaxis_title="Score",
                      title={"text": "Top HN Stories", "x": 0.5, "xanchor": "center"})
    fig.write_html("hn_top.html")
    print(f"\n已生成 hn_top.html（{len(titles)} 条）")
else:
    print("没有拿到可用数据，跳过画图")
```

### 示例 6：把「请求 → JSON → 取字段」拆成纯函数（api_pipeline.py）

示例 1–5 的取数代码都长在 `try/except` 里，一旦没有网络就没法验证「取字段对不对」。真正的工程做法是把链路拆成三段**纯函数**：`parse_items(payload)` 只吃字典、`collect(get_json, ...)` 只吃「一个能取页的函数」、`get_json_with_retry(fetch, ...)` 只吃「一个会失败的调用」。这样用一份假 payload 就能把整条链路测干净——**网络只在最外层出现一次**。这也是练习 17-1/17-3 的骨架。

```python
# api_pipeline.py —— 请求 → JSON → 取字段：全部拆成纯函数，离线也能测
import time

# ===== 一份"假 payload"，结构和 GitHub search API 的响应一模一样 =====
PAYLOAD_PAGE_1 = {
    "total_count": 4350000,
    "incomplete_results": False,
    "items": [
        {"name": "awesome-python", "stargazers_count": 220000,
         "html_url": "https://github.com/vinta/awesome-python",
         "description": "A curated list", "owner": {"login": "vinta"}},
        {"name": "free-python-games", "stargazers_count": 95000,
         "html_url": "https://github.com/tasnowak/free-python-games",
         "description": None, "owner": {"login": "tasnowak"}},
    ],
}
PAYLOAD_PAGE_2 = {
    "total_count": 4350000,
    "items": [
        {"name": "django", "stargazers_count": 78000,
         "html_url": "https://github.com/django/django",
         "description": "Web framework", "owner": {"login": "django"}},
        {"name": "awesome-python", "stargazers_count": 220000,   # ★ 跨页重复
         "html_url": "https://github.com/vinta/awesome-python",
         "description": "A curated list", "owner": {"login": "vinta"}},
    ],
}


def parse_items(payload):
    """★ 纯函数：输入一个 payload，输出五个平行列表。不碰网络、不碰文件。"""
    names, stars, urls, owners, descs = [], [], [], [], []
    for item in payload.get("items", []):
        names.append(item["name"])                       # 核心结构，缺了就报错
        stars.append(item.get("stargazers_count", 0))    # 可选字段用 .get
        urls.append(item.get("html_url", ""))
        owners.append(item.get("owner", {}).get("login", "未知"))
        descs.append(item.get("description") or "（没写简介）")
    return names, stars, urls, owners, descs


names, stars, urls, owners, descs = parse_items(PAYLOAD_PAGE_1)
print("=== 第一页解析结果 ===")
for row in zip(names, stars, owners, descs):
    print(f"  {row[0]:<18}{row[1]:>8,}  by {row[2]:<10}{row[3]}")

print("\n=== 分页循环：一个函数取多页，按名字去重 ===")


def collect(get_json, pages=2, per_page=2, pause=0.0):
    """参数是「取一页的函数」，所以换成假数据也能测。"""
    seen, merged = set(), []
    for page in range(1, pages + 1):
        if pause:
            time.sleep(pause)                            # 真项目里写 pause=1
        payload = get_json(page, per_page)
        if payload is None:
            print(f"  第 {page} 页失败，跳过")
            continue
        page_items = payload.get("items", [])
        for item in page_items:
            if item["name"] in seen:                     # ★ 跨页重复很常见
                print(f"  第 {page} 页发现重复：{item['name']}，丢弃")
                continue
            seen.add(item["name"])
            merged.append(item)
        print(f"  第 {page} 页：返回 {len(page_items)} 条，累计 {len(merged)} 条")
    return merged


FAKE_PAGES = {1: PAYLOAD_PAGE_1, 2: PAYLOAD_PAGE_2}


def fake_get_json(page, per_page):
    return FAKE_PAGES.get(page)


merged = collect(fake_get_json)
n, s, u, o, d = parse_items({"items": merged})
for name, star in sorted(zip(n, s), key=lambda pair: pair[1], reverse=True):
    print(f"  {name:<18}{star:>8,}")

print("\n=== 失败重试：同一个请求最多试 3 次 ===")


def get_json_with_retry(fetch, attempts=3):
    """fetch() 返回 None 表示失败；成功就立刻返回，别做无意义的等待。"""
    for attempt in range(1, attempts + 1):
        payload = fetch()
        if payload is not None:
            print(f"  第 {attempt} 次成功")
            return payload
        print(f"  第 {attempt} 次失败，{'重试' if attempt < attempts else '放弃'}")
    return None


calls = {"n": 0}


def flaky():
    """前两次装死，第三次才成功——模拟网络抖动。"""
    calls["n"] += 1
    return PAYLOAD_PAGE_2 if calls["n"] >= 3 else None


result = get_json_with_retry(flaky)
print("  最终拿到：", [item["name"] for item in result["items"]])
print("  说明：403 不要重试（配额已空，重试只会更糟），网络异常才重试。")
```

**运行结果**（实跑输出）：

```text
=== 第一页解析结果 ===
  awesome-python     220,000  by vinta     A curated list
  free-python-games   95,000  by tasnowak  （没写简介）

=== 分页循环：一个函数取多页，按名字去重 ===
  第 1 页：返回 2 条，累计 2 条
  第 2 页发现重复：awesome-python，丢弃
  第 2 页：返回 2 条，累计 3 条
  awesome-python     220,000
  free-python-games   95,000
  django              78,000

=== 失败重试：同一个请求最多试 3 次 ===
  第 1 次失败，重试
  第 2 次失败，重试
  第 3 次成功
  最终拿到： ['django', 'awesome-python']
  说明：403 不要重试（配额已空，重试只会更糟），网络异常才重试。
```

三条解读：

1. **参数传「函数」而不是「网址」，是这个示例最值钱的设计**。`collect(get_json)` 里的 `get_json` 可以是真 requests，也可以是 `fake_get_json`——**依赖从外部注入，测试就不用联网**。Django 的测试客户端、pytest 的 mock 都是这个思路。
2. **「重试」和「限速」是两件事，不能混**。`get_json_with_retry` 处理的是「这次调用意外失败」（网络抖动、超时），所以连试 3 次；而 403 是**确定性失败**，重试只会继续消耗已经为 0 的配额。把两者混成一个大 `while` 循环，就是新手最常见的「死循环轰炸 API」。
3. **把 `pages=2` 改成 `pages=6` 会怎样**：`FAKE_PAGES` 只有两页，第 3–6 页会依次打印「第 N 页失败，跳过」，`merged` 仍是 3 条——**这正是真实翻页到底后该有的行为**：不该崩，也不该静默。若把 `per_page` 改成 100，`page_params` 里应同步检查「超过 100 会被 API 截断」。

---

### 示例 7：查询串与响应的最小闭环

没有网也能验证「发什么、收什么」：把 URL 与响应都写成字符串，先测解析，再谈请求。

```python
from urllib.parse import urlencode, parse_qs, urlparse

params = {"q": "python 课程", "sort": "stars", "per_page": 5}
url = "https://api.example.com/search?" + urlencode(params)
print("请求 URL:", url)
print("解析回来:", parse_qs(urlparse(url).query)["q"][0])
print("参数个数:", len(parse_qs(urlparse(url).query)))
```

运行结果：

```text
请求 URL: https://api.example.com/search?q=python+%E8%AF%BE%E7%A8%8B&sort=stars&per_page=5
解析回来: python 课程
参数个数: 3
```

### 示例 8：Plotly 的 data 结构长什么样

Plotly 的图本质就是一个字典列表；先在本地把结构拼对、断言长度一致，再交给库去画。

```python
data = [{"type": "bar", "orientation": "h",
         "x": [68000, 12000], "y": ["flask", "django"]}]
layout = {"title": "Star 数对比", "xaxis": {"title": "stars"}}

assert data[0]["type"] == "bar"
assert len(data[0]["x"]) == len(data[0]["y"])
print("系列数:", len(data), "| 数据点:", len(data[0]["x"]))
print("标题:", layout["title"], "| 轴标题:", layout["xaxis"]["title"])
```

运行结果：

```text
系列数: 1 | 数据点: 2
标题: Star 数对比 | 轴标题: stars
```

---

## 四、动手练习

### 基础档

**练习 17-1【API 网址解析器与响应字典解剖】**
写 `api_url_parser.py`：
1. 定义三个网址常量：GitHub search API、HN 列表 API、HN 详情 API（用 `{}` 占位）；写 `split_query(url)` 返回 `(路径, {参数名: 参数值})`，没有问号时参数字典为空
2. 对 GitHub 那个网址调用它并逐行打印参数；再用 `requests.Request(...).prepare().url` 把 `params` 拼成网址
3. 构造一份**离线**响应字典（4 个仓库，其中一个 `description` 为 `None`、一个缺 `forks_count`），提取成 6 个平行列表；`description` 兜底成「（没写简介）」，fork 数用 `.get("forks_count", 0)` 取；按 star 排序并加 `assert` 检查等长
4. **验收**：打印出的参数和你手写的一致；输出里看不到任何 `None`；排序第一行是 star 最多的那个；能说出 `q` 和 `sort` 各控制什么

**练习 17-2【API 观测台】**
写 `api_watchtower.py`：`probe(url, headers=None)` 返回 `(状态码, 剩余配额, 响应前 100 字)`，网络异常返回 `(-1, None, 异常信息)`；对三个地址各调一次并打印（GitHub 搜索接口、一个不存在的路径、HN 列表接口）；`diagnose(code)` 把状态码翻成中文诊断（至少覆盖 200 / 403 / 404 / -1）。
**验收**：第二个地址大概率返回 404 或 403 且 `diagnose` 说对；**完全断网也不崩**，能打印出三条 `-1`

### 进阶档

**练习 17-3【★ 可点击的仓库榜（带缓存与兜底）】**
写 `clickable_chart.py`：写 `fetch_top_repos()` 调 GitHub search API，**必须**含 `Accept` 头、`timeout`、`try/except`、`status_code` 检查，失败返回 `None` 并打印原因；`None` 时切到内置 `SAMPLE_ITEMS`，成功后把响应存成 `github_repos.json`，下次**优先读缓存**（读文件也包 `try/except`）。把列表装进 `pd.DataFrame`（`custom_data` 传列名时必须有 DataFrame），用 `custom_data=["html_url"]` 挂链接，`hovertemplate` 显示加粗仓库名、star 数、`Open in GitHub` 可点击链接，加 `<extra></extra>`；用 `color="owner"` + `color_discrete_map` 上固定色；存成 HTML 后浏览器**逐个悬停点一遍**。
**验收**：做 6 根柱子，其中一根「诱饵」的 `html_url` 是空字符串——它的链接区域空白且点不动。由此说清「为什么有些链接点不动」以及怎么兜底（提示：url 为空时兜底成讨论页，或不放 `<a>` 标签）

**练习 17-4【Hacker News 摘要机】**
写 `hn_digest.py`：两段式调用（`topstories.json` 拿 id → 只对前 10 个请求 `item/{id}.json`），请求之间 `time.sleep(1)`，失败要打印原因并 `continue` 不能静默跳过；处理脏数据（条目 `null`、`title` 缺失、`url` 为 `null` 用讨论页兜底）；提取 `title`/`score`/`by`（★ 不能当变量名）/`descendants`；画条形图（x 是截断到 30 字符的标题，悬停框显示作者、评论数、可点击链接）。
**验收**：柱子数 = 10 −（被删除或失败的条数）；能用一句话解释为什么 x 轴标签要自己截断。

---

## 五、参考答案

### 参考答案 17-1

```python
# api_url_parser.py —— 拆解网址 + 解剖响应字典（不发网络请求）
import requests

GITHUB_SEARCH = "https://api.github.com/search/repositories?q=language:python&sort=stars"


def split_query(url):
    """返回 (路径, {参数名: 参数值})；没有问号时参数为空字典。"""
    if "?" not in url:
        return url, {}
    path, _, query = url.partition("?")
    params = {}
    for pair in query.split("&"):
        key, _, value = pair.partition("=")
        params[key] = value
    return path, params


path, params = split_query(GITHUB_SEARCH)
print("路径：", path, "| 参数：", params)   # q = 语言条件，sort = 按 star 排序
print("用 params 拼网址：",
      requests.Request("GET", "https://api.github.com/search/repositories",
                       params=params | {"per_page": 5}).prepare().url)

# ===== 响应字典解剖（离线）=====
# 故意造两种脏数据：免费游戏那个 description 为 None，flask 缺 forks_count
RAW = [("awesome-python", 220000, "vinta", "A curated list", 23000),
       ("free-python-games", 95000, "tasnowak", None, 7000),
       ("django", 78000, "django", "Web framework", 31000),
       ("flask", 67000, "pallets", "Micro framework", None)]
items = [{"name": n, "stargazers_count": s, "owner": {"login": o},
          "html_url": f"https://github.com/{o}/{n}", "description": d,
          **({"forks_count": f} if f is not None else {})} for n, s, o, d, f in RAW]
print("\ntotal_count：4200000（总命中数，不是返回条数）")

names, stars, logins, descs, forks, urls = [], [], [], [], [], []
for r in items:
    names.append(r["name"])
    stars.append(r["stargazers_count"])
    urls.append(r["html_url"])
    logins.append(r["owner"]["login"])
    descs.append(r["description"] or "（作者很懒，没写简介）")
    forks.append(r.get("forks_count", 0))           # 字段可能不存在

for row in zip(names, stars, logins, forks, descs):
    print(f"{row[0]:<18}{row[1]:>9,}  by {row[2]:<10}fork={row[3]:>7,}  {row[4]}")
for rank, i in enumerate(sorted(range(len(stars)),
                                key=lambda i: stars[i], reverse=True), 1):
    print(f"{rank}. {names[i]:<18}{stars[i]:>9,}  {urls[i]}")

assert len(names) == len(stars) == len(logins) == len(descs) == len(forks) == len(urls)
print("\n六个列表等长：True；没有 None：", all(d is not None for d in descs))
```

### 参考答案 17-2

```python
# api_watchtower.py —— 状态码观测台
import requests

ACCEPT = {"Accept": "application/vnd.github+json"}
URLS = [("GitHub 搜索", "https://api.github.com/search/repositories?q=language:python&sort=stars", ACCEPT),
        ("不存在的路径", "https://api.github.com/not-a-real-endpoint-xyz", ACCEPT),
        ("HN 列表", "https://hacker-news.firebaseio.com/v0/topstories.json", None)]
DIAGNOSIS = {200: "成功，可以放心调 response.json()",
             403: "被拒绝：多半是速率限制超了，或需要认证",
             404: "网址或资源 ID 写错了",
             429: "请求太多被限流，等一会儿再来",
             500: "服务器内部错误，隔一会儿重试",
             -1: "网络没通：断网或超时"}


def probe(url, headers=None):
    """返回 (状态码, 剩余配额, 响应前 100 字)。网络异常返回 (-1, None, 原因)。"""
    try:
        response = requests.get(url, headers=headers or {}, timeout=10)
    except requests.exceptions.RequestException as error:
        return -1, None, f"{type(error).__name__}: {error}"
    return (response.status_code, response.headers.get("X-RateLimit-Remaining"),
            response.text[:100])


for label, url, headers in URLS:
    code, remaining, snippet = probe(url, headers)
    print(f"\n[{label}] 状态码={code} 剩余配额={remaining}")
    print("  诊断：", DIAGNOSIS.get(code, f"没见过的状态码 {code}"))
    print("  片段：", snippet.replace("\n", " ")[:100])

print("\n说明：未认证每小时 60 次；配额看响应头 X-RateLimit-Remaining。")
```

### 参考答案 17-3

```python
# clickable_chart.py —— 带缓存兜底的可点击仓库榜
# 跑完生成 clickable.html 和 github_repos.json，可以删掉
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import requests

CACHE = Path("github_repos.json")
HEADERS = {"Accept": "application/vnd.github+json"}
# 最后一行的 html_url 是空字符串（诱饵），用来验证链接点不动的情况
RAW = [("awesome-python", 220000, "vinta"), ("django", 78000, "django"),
       ("flask", 67000, "pallets"), ("诱饵仓库", 5000, "nobody")]
SAMPLE_ITEMS = [
    {"name": n, "stargazers_count": s, "owner": {"login": o}, "description": f"示例 {n}",
     "html_url": "" if n == "诱饵仓库" else f"https://github.com/{o}/{n}"}
    for n, s, o in RAW]


def fetch_top_repos(count=10):
    """调用 GitHub search API；失败返回 None（并打印原因）。"""
    params = {"q": "language:python", "sort": "stars", "per_page": count}
    try:
        response = requests.get("https://api.github.com/search/repositories",
                                headers=HEADERS, params=params, timeout=10)
    except requests.exceptions.RequestException as error:
        print(f"网络请求失败：{error}")
        return None
    if response.status_code != 200:
        print("状态码", response.status_code, "配额",
              response.headers.get("X-RateLimit-Remaining"))
        return None
    CACHE.write_text(response.text, encoding="utf-8")      # 存缓存供下次用
    return response.json()["items"]


def load_cache():
    """读缓存；文件不存在或内容坏了都返回 None。"""
    try:
        return json.loads(CACHE.read_text(encoding="utf-8"))["items"]
    except (OSError, ValueError, KeyError) as error:
        print(f"没有可用缓存（{type(error).__name__}）")
        return None


items = load_cache() or fetch_top_repos()      # 优先读缓存，没有再请求网络
if items is None:
    print("当前使用示例数据（没有网络）")
    items = SAMPLE_ITEMS

df = pd.DataFrame({"name": [r["name"] for r in items],
                   "stars": [r["stargazers_count"] for r in items],
                   "description": [r["description"] or "（没写简介）" for r in items],
                   "owner": [r["owner"]["login"] for r in items],
                   "html_url": [r["html_url"] for r in items]})

fig = px.bar(
    df, x="name", y="stars", hover_name="name",
    hover_data=["description", "owner"],
    custom_data=["html_url"],                     # ★ 把链接挂到柱子上
    color="owner",
    color_discrete_map={"vinta": "seagreen", "django": "green",
                        "pallets": "darkorange", "nobody": "gray"},
    text_auto=".2s",
    title="Most-Starred Python Repositories",
)
fig.update_traces(marker_line_width=1.5,
                  hovertemplate="<b>%{hovertext}</b><br>Stars: %{y:,}<br>"
                                "<a href='%{customdata[0]}'>Open in GitHub</a>"
                                "<extra></extra>")
fig.update_layout(
    title={"text": "Most-Starred Python Repositories", "x": 0.5, "xanchor": "center"},
    xaxis_title=None, yaxis_title="Stars")
fig.write_html("clickable.html")

print("已生成 clickable.html —— 「诱饵仓库」的 html_url 是空字符串，链接空白且点不动。")
print("解法：url 为空时兜底成讨论页，或不放 <a> 标签只显示纯文本。")
```

### 参考答案 17-4

```python
# hn_digest.py —— Hacker News 两段式调用
# 跑完生成 hn_digest.html，可以删掉
import time

import pandas as pd
import plotly.express as px
import requests

TOP_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{id}.json"
TOP_N = 10


def get_json(url):
    """try/except + 状态码检查，失败返回 None。"""
    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.RequestException as error:
        print(f"  请求失败：{type(error).__name__}")
        return None
    if response.status_code != 200:
        print(f"  状态码 {response.status_code}，跳过")
        return None
    return response.json()


story_ids = get_json(TOP_URL)          # ===== 第一段：拿 id 列表 =====
titles, scores, authors, comments, links = [], [], [], [], []
skipped = 0

if not story_ids:
    print("拿不到列表，程序结束（网络不通时不画图，也不崩）")
else:
    print(f"第一段：{len(story_ids)} 个 id，只处理前 {TOP_N} 个")
    for index, story_id in enumerate(story_ids[:TOP_N]):   # ===== 第二段：逐个取详情 =====
        if index > 0:
            time.sleep(1)                 # 主动限速
        item_dict = get_json(ITEM_URL.format(id=story_id))
        # None = 网络/状态码问题；返回 JSON null = 条目已被删除，两种都要 continue
        if not isinstance(item_dict, dict):
            print(f"  id {story_id} 请求失败或已删除，跳过")
            skipped += 1
            continue
        titles.append(item_dict.get("title") or "(无标题)")
        scores.append(item_dict.get("score", 0))
        # ★ "by" 是合法 JSON 键，但 by 是 Python 关键字，只能直接取值
        authors.append(item_dict.get("by", "匿名"))
        comments.append(item_dict.get("descendants", 0))
        links.append(item_dict.get("url")          # ★ url 可能是 null，兜底讨论页
                     or f"https://news.ycombinator.com/item?id={story_id}")

if titles:
    print(f"\n成功 {len(titles)} 条，跳过 {skipped} 条")
    # x 轴标签自己截断到 30 字符，否则标签互相重叠看不清
    labels = [t if len(t) <= 30 else t[:29] + "…" for t in titles]
    df = pd.DataFrame({"title": labels, "score": scores, "author": authors,
                       "comments": comments, "link": links})
    fig = px.bar(df, x="title", y="score", hover_name="title",
                 custom_data=["author", "comments", "link"],
                 title="Top Hacker News Stories")
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>by %{customdata[0]}<br>Score: %{y:,}<br>"
                      "Comments: %{customdata[1]}<br>"
                      "<a href='%{customdata[2]}'>Read</a><extra></extra>")
    fig.update_layout(xaxis_title=None, yaxis_title="Score",
                      title={"text": "Top Hacker News Stories",
                             "x": 0.5, "xanchor": "center"},
                      xaxis={"tickangle": -30})   # 标签斜一点，少重叠
    fig.write_html("hn_digest.html")
else:
    print("没有可用数据，跳过画图")
```

---

## 六、本单元验收自测

**1. 简答题**：用「餐厅服务员」类比解释 API。`response.status_code` 和 `response.json()` 分别对应什么？
> **要点**：`requests.get()` 是报菜名；`status_code` 是**确认信号**——200「做好了」、404「菜单上没这道」、403「厨房不接这单」；`.json()` 是**上菜**，把响应体文本加工成数据结构。★ 顺序永远是**先 status_code 再 json()**，因为端回来的还有「售罄通知书」（合法 JSON、内容全是错误信息）。

**2. 判断题**：`response_dict["total_count"]` 就是 GitHub search API 这次返回的仓库数量。
> **要点**：错误。`total_count` 是**符合搜索条件的总数**（几百万个），`len(response_dict["items"])` 才是**这次实际返回给你的条数**（默认 30 条）。杀伤力：你会误以为拿到了几百万条，然后在 `items` 上统计出一个莫名其妙的数字。

**3. 简答题**：GitHub 未认证的速率限制是多少？怎么在**发请求之前**就知道该不该发？被限流了该怎么做？
> **要点**：未认证**每小时 60 次**（认证后 5000 次）。查响应头 `response.headers["X-RateLimit-Remaining"]`（`X-RateLimit-Limit` 显示总配额），Header 大小写不敏感。被限流返回 **403**（有时 **429**）。正确做法：**打印原因，主动停止，不要死循环重试**（重试只会浪费配额并延长封禁），等配额窗口重置或改用认证；连续取数据时主动 `time.sleep(1)`。配额按「一小时窗口」算，发出 3 次后应看到 57 而不是 60。

**4. 简答题**：`hovertemplate` 里的 `%{customdata[0]}` 对应 `<a>` 标签的哪一部分？为什么链接文字常常是写死的？
> **要点**：对应 `<a href='...'>` 里的**地址**。HTML 链接写作 `<a href='地址'>显示文字</a>`，属性值和显示文字是两个独立的部分。教材把 `html_url` 在 `custom_data` 里放两遍分别填这两处，但新版 plotly 不允许重复列名（`DuplicateError`），所以只传一列填 `href`、文字写死成 "Open in GitHub"。**写之前先把列和索引一一对齐**，不确定就先 `print([list(r) for r in fig.data[0].customdata])` 看清楚。

**5. 改错题**：下面两段代码各有多处错误，先自己找，再看解析。

```python
# INTENTIONALLY-BROKEN 演示用：下面这段故意写错，请自己找出来
import requests

url = "https://api.github.com/search/repositories?q=language:python&sort=stars"
response = requests.get(url, headers={"Accept": "application/vnd.github+json"})
response_dict = response.json()
for repo in response_dict["items"]:
    print(repo["name"], repo["stargazers_count"], repo["description"])

import plotly.express as px
fig = px.bar(x="name", y="stargazers_count")      # 少了 DataFrame，px 认不出列名
fig.update_traces(hovertemplate="<b>%{customdata[0]}</b><extra></extra>")
fig.write_html("repos.html")
```

```python
# INTENTIONALLY-BROKEN 演示用：下面这段故意写错，请自己找出来
import requests

story_ids = requests.get(
    "https://hacker-news.firebaseio.com/v0/topstories.json").json()
for index, story_id in enumerate(story_ids):
    data = requests.get(
        f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json").json()
    by = data["by"]
    titles.append(data["title"])
```

> **要点**：第一段五处问题——① 没有 `try/except`，网络一断就崩；② 没检查 `status_code`，403 时 `.json()` 照样成功，你拿到的是一段「错误说明」JSON，然后 `response_dict["items"]` 抛 `KeyError`；③ `description` 可能是 `None`，该写 `repo["description"] or "（没写简介）"`；④ 只画了 `items[0]`，应先提取成平行列表装进 DataFrame；⑤ 用了 `%{customdata[0]}` 却没传 `custom_data`，占位符取不到值。
> 第二段四处问题——① 没有 `try/except` 和状态码检查；② 500 个 id 全部串行请求、**没有限速**，几秒就打光 60 次配额然后吃 403，必须 `story_ids[:10]` 切片 + `time.sleep(1)`；③ `by = data["by"]` 是**语法错误**（`by` 是 Python 关键字），只能写 `authors.append(data["by"])`；④ `titles` 列表根本没初始化就 `append`。

**6. 简答题**：Hacker News 的「两段式调用」是什么意思？`item/{id}.json` 返回 `null` 时该怎么处理？
> **要点**：第一段请求 `topstories.json` 拿到一串 id（只有数字）；第二段对每个 id 请求 `item/{id}.json` 拿详情。这么设计**省流量又通用**：一份 id 列表能配不同详情查询，组合出「当前最热」「某作者的帖子」等成百上千种需求。返回 `null`（Python 的 `None`）表示条目已删除，必须 `if not isinstance(item_dict, dict): continue` 检查，否则 `item_dict["title"]` 抛 `TypeError`；这属于「失败的请求」，要**打印出来**，不能静默跳过。

---

## 七、常见错误清单（务必逐条自查）

### 错误 1：不检查状态码就 `.json()`

**症状**：`JSONDecodeError`，或者拿到 `{"message": "rate limit"}` 还在解析。
**原因**：4xx/5xx 的响应体不是你要的数据。
**改法**：先 `if r.status_code != 200:` 打印状态与响应前 200 字，再决定是否解析；或 `r.raise_for_status()`。

### 错误 2：没设超时，程序一直挂着

**症状**：脚本卡住不动，也不报错。
**原因**：`requests.get(url)` 默认不超时（可能等几分钟）。
**改法**：`requests.get(url, timeout=10)`；批量抓取时循环里加 `time.sleep(0.5)`。

### 错误 3：只取了第一页

**症状**：明明有 1000 条，只拿到 30 条。
**原因**：分页参数没处理。
**改法**：看响应里的 `next`/`Link` 头或 `page` 字段，循环取到没有下一页为止。

### 错误 4：直接 `data["items"]` → 偶尔 KeyError

**症状**：平时正常，偶尔崩一次。
**原因**：接口在出错/限流时返回的字段不一样。
**改法**：`data.get("items", [])`；每个 item 也用 `.get("name", "?")`。

### 错误 5：被 403/429 拦了还继续打

**症状**：越跑越慢，最后全 429。
**原因**：请求太密，触发限流。
**改法**：读 `Retry-After` 头、加 `time.sleep` 退避（1s→2s→4s）；带上 `User-Agent`，别裸奔。

---

## 本单元小结与产出检查

- [ ] 能用「餐厅服务员」类比说清 API，解释「不必知道厨房怎么做」
- [ ] 能默写 `requests.get(url, headers=..., timeout=10)`，说出 `status_code`/`text`/`headers`/`json()` 各自作用
- [ ] 说出 200/403/404/429/500 各自意味着什么，以及「先 status_code 再 .json()」的原因
- [ ] 能写出完整的 `try/except` + 状态码检查模板，说出「失败请求要打印而不是静默跳过」的理由
- [ ] 调用 GitHub search API 时能带对 `Accept: application/vnd.github+json`，从 `items` 取出 `name`/`stargazers_count`/`html_url`/`description`/`owner.login`
- [ ] 能用 `X-RateLimit-Remaining` 查配额，说出「未认证每小时 60 次、超限 403」，知道要主动 `sleep` 限速、存缓存
- [ ] 能用 `px.bar` 画仓库条形图，`hover_data` 定制悬停、`color_discrete_map` 定制颜色
- [ ] 能用 `custom_data` + `hovertemplate` 做出**可单击的链接**，说清 `customdata[n]` 索引与 `<a href>` 的对应
- [ ] 能说清 Hacker News 两段式调用：先 `topstories.json` 拿 id，再 `item/{id}.json` 拿详情
- [ ] 练习 17-1、17-3、17-4 已跑通；17-3 已用浏览器验证过链接能点

**下一单元预告**：单元 18 进入项目 3「Django」。前两个单元我们一直站在「客户端」这一侧——自己发请求、自己处理数据、自己画图，画完存成 HTML 发给别人看。Django 让你站到「服务端」这一侧：用 Python 写一个**能被别人访问的网站**——有首页、有 URL、有表单、有数据库。你会第一次遇到「这个文件改了会影响什么」这类新困惑。
