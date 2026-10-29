# -*- coding: utf-8 -*-
"""《流畅的 Python（第 2 版）》精读课 —— 站点构建器。

与入门课共用一套渲染思路（markdown → Pygments → 静态页），但完全独立：
  course-fluent/*.md  →  fluent/web/NN.html        单元讲义
                      →  fluent/web/lessons/*.html 课节页
                      →  fluent/web/bank.html      题库
                      →  fluent/web/gates.html     关卡验收
                      →  fluent/web/ppt/index.html 大纲课件
                      →  fluent/index.html         课程首页

用法：
  C:/Users/57411/.workbuddy/binaries/python/envs/default/Scripts/python.exe tools/build_fluent.py
"""
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "course-fluent")
OUT = os.path.join(ROOT, "fluent")
WEB = os.path.join(OUT, "web")
sys.path.insert(0, HERE)

import build_lectures as bl          # noqa: E402  markdown 转换 / 高亮

# 深色代码块配 default 亮色主题会发灰，这里统一换成 monokai（只影响本构建器）
_HF = bl.HtmlFormatter
bl.HtmlFormatter = lambda **kw: _HF(style="monokai",
                                    **{k: v for k, v in kw.items() if k != "style"})

UNIT_META = {
    1:  ("第 1–2 章", "1–2 周", "数据模型 · 序列 · 推导式 · 切片"),
    2:  ("第 3–4 章", "1–2 周", "哈希表 · 映射类型 · Unicode · 编解码"),
    3:  ("第 5–6 章", "1–2 周", "dataclass · 具名元组 · 引用 · 可变性"),
    4:  ("第 7–8 章", "1–2 周", "一等函数 · 高阶函数 · 类型提示"),
    5:  ("第 9–10 章", "1–2 周", "闭包 · 装饰器 · 策略与命令模式"),
    6:  ("第 11–12 章", "1–2 周", "对象表示 · 可哈希 · 序列协议"),
    7:  ("第 13–14 章", "1–2 周", "鸭子类型 · 协议 · ABC · 多重继承"),
    8:  ("第 15–16 章", "1–2 周", "泛型 · 型变 · 运算符重载"),
    9:  ("第 17–18 章", "1–2 周", "迭代器 · 生成器 · with · match"),
    10: ("第 19–20 章", "1–2 周", "GIL · 线程池 · 进程池 · Executor"),
    11: ("第 21 章", "1–2 周", "协程 · 任务 · 异步 IO · 异步迭代"),
    12: ("第 22–24 章", "2–4 周", "动态属性 · 描述符 · 元类"),
}

BOOK = json.load(open(os.path.join(SRC, "bookmap.json"), encoding="utf-8"))

# 由 main 用 fluent_syllabus.totals() 填：两种配速总周数（侧栏/首页/搜索共用）
SYL_TXT = "标准 12 周 / 轻量 24 周"

# 题库数量一律由 bank.json 推出来，别再写死（写死过 36，加题后要改 8 处）
BANK = json.load(open(os.path.join(SRC, "bank.json"), encoding="utf-8"))
BANK_N = len(BANK)
BANK_PER_UNIT = {}
for _q in BANK:
    BANK_PER_UNIT[_q["unit"]] = BANK_PER_UNIT.get(_q["unit"], 0) + 1
SYL_RANGE = "12–24"

# 24 章「设计取舍」长文 → 单元映射（side_block / 课节页侧栏要用，构建早期就加载）
DESIGN = os.path.join(SRC, "design")
DESIGN_META = json.load(open(os.path.join(DESIGN, "chapters.json"),
                            encoding="utf-8"))["chapters"]

# 12 篇「源码走读」：每单元一个可运行程序 + 逐段讲解（输出由 check_walk.py 实跑写回）
WALK = os.path.join(SRC, "walk")

LESSONS_PER_UNIT = 4

# 教材五部分 → 单元分组（首页按此分区展示）
PARTS = [
    ("第一部分 · 数据结构", "第 1–6 章", [1, 2, 3]),
    ("第二部分 · 函数即对象", "第 7–10 章", [4, 5]),
    ("第三部分 · 类和协议", "第 11–16 章", [6, 7, 8]),
    ("第四部分 · 控制流", "第 17–21 章", [9, 10, 11]),
    ("第五部分 · 元编程", "第 22–24 章", [12]),
]

GATE1 = [
    ("u1", "能自定义一个类，支持 len / 索引 / 切片 / for / repr，并解释调用链"),
    ("u1", "能用 listcomp 与 genexp 各写一版等价代码，并说明内存差异"),
    ("u2", "能解释 dict 的键为什么必须可哈希，以及插入顺序为何被保留"),
    ("u2", "能复现并修复一次 UnicodeDecodeError，说明 bytes 与 str 的边界"),
    ("u3", "能用 @dataclass 定义带默认值、后处理与冻结选项的值对象"),
    ("u3", "能解释浅拷贝、深拷贝与函数传参的引用语义"),
    ("u4", "能把函数当参数/返回值传递，并用 operator / functools 简化代码"),
    ("u4", "能给公开函数写全参数与返回值注解，并通过 mypy 检查"),
    ("u5", "能徒手写出一个带参数的装饰器，并保留被装饰函数的元数据"),
    ("u5", "能用闭包 + 装饰器重构一段策略分支代码"),
    ("u6", "能实现 __repr__ / __eq__ / __hash__ 三者自洽的值类型"),
    ("u6", "能实现一个可切片、可迭代、可格式化的自定义序列"),
]

GATE2 = [
    ("u7", "能区分鸭子类型、静态协议与 ABC，并为同一接口各写一版实现"),
    ("u7", "能画出一次多重继承的 MRO，并解释 super() 的协作式调用"),
    ("u8", "能用 TypeVar / Generic / Protocol 写出可被类型检查器接受的泛型代码"),
    ("u8", "能为自定义类型实现 +、*、@、比较运算符且不破坏交换律"),
    ("u9", "能手写生成器函数与 yield from，说明惰性求值的收益与代价"),
    ("u9", "能实现上下文管理器，并用 match 解构嵌套数据结构"),
    ("u10", "能解释 GIL 对 CPU 密集与 IO 密集任务的不同影响"),
    ("u10", "能用 concurrent.futures 改写串行下载并处理异常与超时"),
    ("u11", "能写出 asyncio 并发任务，正确使用 gather / TaskGroup 与超时"),
    ("u11", "能说明协程、线程、进程三者的适用边界"),
    ("u12", "能用 __getattr__ / property / 描述符分别实现动态属性"),
    ("u12", "能读懂一个元类，并判断何时该用 __init_subclass__ 代替它"),
]

# ────────────────────────────── 解析 ──────────────────────────────

def load_units():
    units = []
    for fn in sorted(os.listdir(SRC)):
        m = re.match(r"^(\d\d)-单元(\d+)-(.+)\.md$", fn)
        if not m:
            continue
        no = int(m.group(2))
        md = open(os.path.join(SRC, fn), encoding="utf-8").read()
        # 标题以讲义 H1 为准（文件名不能带「、」，会丢标点）
        h1 = re.search(r"(?m)^#\s+单元\s*\d+\s*[·:：]\s*(.+)$", md)
        title = h1.group(1).strip() if h1 else m.group(3)
        units.append({"no": no, "title": title, "md": md,
                      "file": fn, **parse_unit(md)})
    units.sort(key=lambda u: u["no"])
    for i, u in enumerate(units, 1):
        if u["no"] != i:
            raise SystemExit(f"单元编号不连续：期望 {i}，实际 {u['no']}（{u['file']}）")
        if len(u["lessons"]) != LESSONS_PER_UNIT:
            raise SystemExit(f"单元 {u['no']} 有 {len(u['lessons'])} 节，应为 {LESSONS_PER_UNIT} 节")
        for L in u["lessons"]:
            g = (u["no"] - 1) * LESSONS_PER_UNIT + L["local"]
            if str(g) not in BOOK:
                raise SystemExit(f"bookmap.json 缺少第 {g} 课的对照")
    return units

CASES = os.path.join(SRC, "cases")

def eff_lines(code):
    """有效代码行：非空且非纯注释。"""
    return sum(1 for l in code.splitlines()
               if l.strip() and not l.strip().startswith("#"))

def load_cases():
    out = {}
    for fn in sorted(os.listdir(CASES)):
        m = re.match(r"^u(\d\d)\.md$", fn)
        if not m:
            continue
        no = int(m.group(1))
        md = open(os.path.join(CASES, fn), encoding="utf-8").read()
        h1 = re.search(r"(?m)^#\s+单元\s*\d+\s*综合案例\s*[·:：]\s*(.+)$", md)
        if not h1:
            raise SystemExit(f"{fn} 缺少「# 单元 N 综合案例 · 标题」")
        title = h1.group(1).strip()
        body = md[h1.end():].strip()
        blocks = re.findall(r"```python\n(.*?)```", body, re.S)
        if len(blocks) != 2:
            raise SystemExit(f"{fn} 应有 2 个 python 代码块（重构前 / 重构后），实际 {len(blocks)}")
        for i, code in enumerate(blocks, 1):
            try:
                compile(code, f"<{fn}#{i}>", "exec")
            except SyntaxError as e:
                raise SystemExit(f"{fn} 第 {i} 个代码块语法错误：{e}")
        lines = [eff_lines(c) for c in blocks]
        if lines[0] < 15 or lines[1] < 25 or sum(lines) < 40:
            raise SystemExit(f"{fn} 太薄：重构前 {lines[0]} 行 / 重构后 {lines[1]} 行")
        if lines[1] < lines[0] * 0.9:
            raise SystemExit(f"{fn} 重构后（{lines[1]} 行）比重构前（{lines[0]} 行）缩水太多")
        out[no] = {"title": title, "body": body, "lines": lines}
    if sorted(out) != list(range(1, 13)):
        raise SystemExit(f"案例应为 u01–u12 共 12 个，实际 {sorted(out)}")
    return out

def attach_cases(units, cases):
    for u in units:
        c = cases[u["no"]]
        if "## 综合案例" in u["outro"]:
            raise SystemExit(f"单元 {u['no']} 的讲义里仍有旧「## 综合案例」段，请删除")
        head = f'## 综合案例：{c["title"]} {{: #case-u{u["no"]:02d} }}'
        u["outro"] = f"{head}\n\n{c['body']}\n\n" + u["outro"]

def parse_unit(md):
    parts = re.split(r"(?m)^## ", md)
    head, sections = parts[0], ["## " + p for p in parts[1:]]
    head = re.sub(r"^#\s+.*\n", "", head, count=1)      # 去掉 H1，标题由页头承担
    lessons, intro_extra, outro = [], [], []
    for sec in sections:
        m = re.match(r"## 第\s*(\d+)\s*课\s*[·:：]\s*(.+)", sec)
        if m:
            body = sec.split("\n", 1)[1] if "\n" in sec else ""
            lessons.append({"local": len(lessons) + 1, "title": m.group(2).strip(),
                            "md": body})
        elif lessons:
            outro.append(sec)
        else:
            intro_extra.append(sec)
    intro = head + "".join(intro_extra)
    # 目标：正文开头第一段 blockquote
    for L in lessons:
        gm = re.search(r"^>\s*本节目标[：:]\s*(.+)$", L["md"], re.M)
        L["goal"] = gm.group(1).strip() if gm else ""
        if gm:
            L["md"] = re.sub(r"^>\s*本节目标[：:].*\n?", "", L["md"], count=1, flags=re.M)
        L["md"] = L["md"].strip()
    return {"intro": intro, "lessons": lessons, "outro": "".join(outro)}

def toc_h2(body_html):
    """单元页目录只取 h2（导入 / 四节课 / 验收），避免侧栏被 h3 撑爆。"""
    items = []
    for m in re.finditer(r'<h2 id="([^"]+)">(.*?)</h2>', body_html, re.S):
        txt = re.sub(r"<[^>]+>", "", m.group(2))
        items.append(f'<a class="lv2" href="#{m.group(1)}">{html.escape(txt)}</a>')
    return "\n".join(items)

def book_box(g, lesson=None):
    b = BOOK.get(str(g))
    if not b:
        return ""
    ext = ""
    if lesson:
        m = re.search(r"(?m)^### 延伸：(.+)$", lesson["md"])
        if m:
            ext = f'<p>本节额外补充：{html.escape(m.group(1).strip())}</p>'
    return (f'<div class="bookbox"><div class="bh"><b>教材对照</b>'
            f'<span>{html.escape(b["book"])}</span>'
            f'<em>本节自足，无需回查原书</em></div>{ext}</div>')

def md2html(md):
    # 任务清单：python-markdown 没有 task-list 扩展，手动换成可勾选的小方块
    md = re.sub(r"(?m)^(\s*)-\s+\[ \]\s+(.+)$",
                r'\1- <span class="ck"></span>\2', md)
    md = re.sub(r"(?m)^(\s*)-\s+\[[xX]\]\s+(.+)$",
                r'\1- <span class="ck on"></span>\2', md)
    return bl.add_heading_ids(bl.convert(md)).replace(
        "<table>", '<div class="tblwrap"><table>').replace(
        "</table>", "</table></div>")

# ────────────────────────────── 样式 ──────────────────────────────

CSS = """
:root{--bg:#f7f7fb;--card:#fff;--line:#e4e4ef;--text:#1a1a2b;--muted:#5a5a70;
--p1:#4c3a9e;--p1bg:#eeebfa;--p2:#0a7d63;--p2bg:#e6f6f0;--p3:#a06009;--p3bg:#fdf3e2;
--p4:#c8443c;--p4bg:#fbeceb;--r:14px}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif;
line-height:1.75}
a{color:var(--p1);text-decoration:none}
a:hover{text-decoration:underline}
.top{position:sticky;top:0;z-index:40;background:rgba(247,247,251,.95);
backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.top-in{max-width:1320px;margin:0 auto;padding:0 22px;height:58px;display:flex;
align-items:center;gap:14px;min-width:0}
.back{font-size:13px;color:var(--muted);white-space:nowrap}
.back:hover{color:var(--p1)}
.top h1{font-size:15.5px;margin:0;font-weight:700;flex:1;min-width:0;overflow:hidden;
text-overflow:ellipsis;white-space:nowrap}
.top .tag{font-size:11px;font-weight:700;padding:3px 9px;border-radius:20px;
background:var(--p1bg);color:var(--p1);white-space:nowrap}
.top .ppt{font-size:12.5px;font-weight:700;color:#8a5a00;background:#fdf3e2;
border:1px solid #f0d8a8;border-radius:6px;padding:4px 10px;white-space:nowrap}
.top .ppt:hover{background:#fbe9cc;text-decoration:none}
.switch{font-size:12.5px;font-weight:700;color:var(--p1);background:var(--p1bg);
border:1px solid #d8d1f2;border-radius:7px;padding:4px 10px;white-space:nowrap}
.switch:hover{background:#e3ddf8;text-decoration:none}

.layout{max-width:1320px;margin:0 auto;padding:24px 22px 80px;display:flex;gap:24px;
align-items:flex-start}
.side{width:248px;flex-shrink:0;position:sticky;top:88px;max-height:calc(100vh - 110px);
overflow-y:auto}
.sblk{background:var(--card);border:1px solid var(--line);border-radius:12px;
padding:16px 14px;margin-bottom:12px}
.sblk h4{margin:0 0 10px;font-size:11.5px;color:var(--muted);letter-spacing:1px;
font-weight:700}
.toc a{display:block;padding:5px 7px;border-radius:6px;font-size:13px;color:#3d3d55;
border-left:2px solid transparent;line-height:1.5}
.toc a:hover{background:#f2f2f9;text-decoration:none}
.toc a.lv3{padding-left:16px;font-size:12.5px;color:var(--muted)}
.toc a.cur{background:var(--p1bg);color:var(--p1);font-weight:600}
a:focus-visible,button:focus-visible{outline:2px solid var(--p1);outline-offset:2px}
.nlist a{display:flex;gap:8px;align-items:flex-start;padding:6px 7px;border-radius:6px;
font-size:12.5px;color:#3d3d55;line-height:1.5}
.nlist a:hover{background:#f2f2f9;text-decoration:none}
.nlist .no{font-size:10.5px;font-weight:700;color:var(--muted);min-width:20px;
flex-shrink:0;padding-top:1px;font-variant-numeric:tabular-nums}
.nlist .tx{min-width:0;overflow-wrap:anywhere;line-height:1.45}
.main li .ck{display:inline-block;width:12px;height:12px;border:1.5px solid #b9b9cf;
border-radius:3px;margin-right:7px;vertical-align:-1px;background:#fff}
.main li .ck.on{background:var(--p2);border-color:var(--p2);position:relative}
.main li .ck.on::after{content:'✓';position:absolute;left:1px;top:-4px;color:#fff;
font-size:11px;font-weight:700}
.nlist a.cur{background:var(--p1bg);color:var(--p1);font-weight:600}
.nlist a.done .no{color:var(--p2)}
.nlist a.done::after{content:'✓';color:var(--p2);font-weight:700;margin-left:auto;
font-size:12px}
.rel a{display:flex;gap:8px;align-items:baseline;padding:5px 6px;border-radius:7px;
color:inherit}
.rel a:hover{background:#f4f2fd;text-decoration:none}
.rel .k{flex:0 0 30px;font-size:11px;font-weight:700;color:#fff;background:var(--p1);
border-radius:4px;text-align:center;line-height:17px}
.rel a:nth-child(2) .k{background:var(--p3)}
.rel a:nth-child(3) .k{background:var(--p2)}
.rel .v{font-size:12px;color:var(--text);line-height:1.45}
.mini{height:7px;background:#e8e8f2;border-radius:99px;overflow:hidden;margin-top:8px}
.mini i{display:block;height:100%;width:0;background:var(--p2);border-radius:99px;
transition:width .2s}
.minitxt{font-size:11.5px;color:var(--muted);margin-top:5px}

.pbar{height:4px;background:#e8e8f2;position:sticky;top:58px;z-index:39}
.pbar i{display:block;height:100%;background:linear-gradient(90deg,var(--p1),var(--p2))}
.main{flex:1;min-width:0;background:var(--card);border:1px solid var(--line);
border-radius:var(--r);padding:32px 38px;overflow-wrap:anywhere}
.bookbox{background:#f7f6fc;border:1px solid #e6e1f6;border-left:4px solid var(--p1);
border-radius:0 10px 10px 0;padding:12px 16px;margin:18px 0 6px;font-size:13.5px;color:#3b3566}
.bookbox .bh{display:flex;align-items:baseline;gap:8px;margin-bottom:3px;flex-wrap:wrap}
.bookbox b{color:var(--p1);font-size:11.5px;letter-spacing:1px}
.bookbox .bh span{font-size:11.5px;color:var(--muted)}
.bookbox .bh em{margin-left:auto;font-style:normal;font-size:11px;
color:#2f7a52;background:#e8f6ee;border:1px solid #cbe9d8;border-radius:20px;padding:1px 8px}
.bookbox p{margin:3px 0}
.lessonlist{display:none;background:#f7f6fc;border:1px solid #ece9f8;border-radius:12px;
padding:14px 16px;margin:26px 0}
.lessonlist h4{margin:0 0 8px;font-size:11.5px;color:var(--muted);letter-spacing:1px;
font-weight:700}
.main h1{font-size:30px;margin:0 0 10px;line-height:1.3;padding-bottom:16px;
border-bottom:2px solid var(--line)}
.main h2{font-size:21px;margin:38px 0 14px;padding-left:13px;
border-left:4px solid var(--p1);line-height:1.4}
.main h3{font-size:16.5px;margin:24px 0 9px;color:var(--p1)}
.main h4{font-size:14.5px;margin:18px 0 7px;color:#3b3b55}
.main p{margin:11px 0}
.main ul,.main ol{margin:11px 0;padding-left:24px}
.main li{margin:6px 0}
.main strong{color:#3b2b86}
.main hr{border:none;border-top:1px dashed var(--line);margin:26px 0}
.main blockquote{margin:14px 0;padding:12px 16px;background:var(--p1bg);
border-left:4px solid var(--p1);border-radius:0 8px 8px 0;color:#3b3566;font-size:14px}
.main blockquote p{margin:4px 0}
.main code,.wrap code{background:#f0f0f5;border-radius:4px;padding:2px 6px;font-size:.88em;
font-family:Consolas,"SFMono-Regular",monospace;color:#0f5a3d}
.main pre,.wrap pre{background:#1f2130;border-radius:10px;padding:0;margin:16px 0;overflow:hidden;
position:relative;max-width:100%}
.main pre code,.wrap pre code{display:block;padding:16px 18px;font-size:13.5px;line-height:1.65;
font-family:Consolas,"SFMono-Regular",monospace;background:none;overflow-x:auto}
.main pre .cl,.wrap pre .cl{position:absolute;top:8px;right:12px;font-size:10.5px;color:#a9aec2;
letter-spacing:.5px;background:rgba(255,255,255,.08);padding:2px 8px;border-radius:4px}
/* 走读页的「运行输出」：浅底、等宽、可横向滚动，和深色代码块区分开 */
.main pre.out,.wrap pre.out{background:#f4f6f4;border:1px solid #d6e2d9;border-left:3px solid var(--p2)}
.main pre.out code,.wrap pre.out code{color:#26402f;font-size:12.8px;line-height:1.7}
.main table{width:100%;border-collapse:collapse;margin:16px 0;font-size:14px}
.main th{background:#f3f2fa;padding:9px 12px;text-align:left;font-size:13px;
color:var(--muted);border:1px solid var(--line);font-weight:600}
.main td{padding:9px 12px;border:1px solid var(--line);vertical-align:top}
.main input[type=checkbox]{transform:scale(1.15);margin-right:6px;accent-color:var(--p2)}
.main hr + h2{margin-top:26px}

.head{border-bottom:2px solid var(--line);padding-bottom:18px;margin-bottom:22px}
.kicker{display:flex;align-items:center;gap:9px;margin-bottom:10px;flex-wrap:wrap}
.kno{background:var(--p1);color:#fff;font-size:12.5px;font-weight:700;padding:4px 12px;
border-radius:20px;letter-spacing:.5px}
.kwk{background:#eef0f5;color:var(--muted);font-size:12.5px;font-weight:600;
padding:4px 11px;border-radius:20px}
.ku{background:var(--p2bg);color:#0a7a5f;font-size:12.5px;font-weight:600;
padding:4px 11px;border-radius:20px}
.head h1{font-size:29px;margin:0 0 10px;border:none;padding:0}
.head .goal{font-size:15px;color:#43435c;margin:0;line-height:1.7}

.goalbox{background:var(--p1bg);border:1px solid #dcd5f5;border-radius:10px;
padding:12px 16px;margin:0 0 20px;font-size:14px;color:#3b3566}
.goalbox b{color:var(--p1)}

.pn{display:flex;gap:12px;margin-top:40px;padding-top:20px;border-top:1px solid var(--line)}
.pn a{flex:1;background:#f5f5fa;border-radius:10px;padding:13px 17px;
border:1px solid var(--line)}
.pn a:hover{background:#ececf6;text-decoration:none;border-color:var(--p1)}
.pn .nx{text-align:right}
.pn small{display:block;font-size:11.5px;color:var(--muted);margin-bottom:3px}
.pn b{font-size:14px;color:var(--text)}

.mark{display:inline-flex;align-items:center;gap:7px;font-size:13px;color:var(--muted);
cursor:pointer;white-space:nowrap}
.mark input{width:17px;height:17px;accent-color:var(--p2);cursor:pointer}
.mark.on span{color:var(--p2);font-weight:700}
pre .cp{position:absolute;top:6px;right:10px;font:inherit;font-size:11.5px;
font-weight:700;color:var(--p1);background:#fff;border:1px solid var(--line);
border-radius:6px;padding:2px 9px;cursor:pointer;opacity:0;transition:opacity .12s}
pre:hover .cp{opacity:1}
pre .cp.ok{color:#fff;background:var(--p2);border-color:var(--p2)}
#toTop{position:fixed;right:22px;bottom:22px;width:42px;height:42px;border-radius:50%;
background:var(--p1);color:#fff;border:none;font-size:18px;cursor:pointer;
box-shadow:0 6px 18px rgba(40,30,80,.25);opacity:0;pointer-events:none;
transition:opacity .18s;z-index:60}
#toTop.on{opacity:1;pointer-events:auto}

/* 首页 */
.wrap{max-width:1200px;margin:0 auto;padding:0 24px 90px}
.hero{position:relative;overflow:hidden;border-radius:20px;margin:26px 0 22px;
background:linear-gradient(135deg,#4c3a9e 0%,#0a7d63 100%);padding:46px 48px 40px;
color:#fff}
.hero::after{content:'';position:absolute;right:-80px;bottom:-150px;width:420px;
height:420px;border-radius:50%;background:rgba(255,255,255,.08)}
.hero>*{position:relative;z-index:1}
.hero .bdg{display:inline-block;background:var(--p3);border-radius:6px;padding:5px 14px;
font-size:12.5px;font-weight:700;letter-spacing:1.5px;margin-bottom:16px}
.hero h1{font-size:38px;margin:0 0 12px;line-height:1.25}
.hero p{font-size:16px;color:#e2ddf5;margin:0 0 24px;max-width:720px}
.st{display:flex;gap:38px;flex-wrap:wrap}
.st b{display:block;font-size:29px;font-weight:700;line-height:1.2}
.st span{font-size:12.5px;color:#cfc8ee}
.csw{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:0 0 22px}
.csw a{display:flex;gap:15px;align-items:center;background:var(--card);
border:1px solid var(--line);border-radius:16px;padding:18px 20px;color:inherit}
.csw a:hover{border-color:var(--p1);text-decoration:none;background:#fbfaff;
box-shadow:0 6px 24px rgba(76,58,158,.08)}
.csw a.on{border-color:var(--p1);box-shadow:0 0 0 3px rgba(76,58,158,.10)}
.csw .ic{width:42px;height:42px;border-radius:12px;background:var(--p1bg);color:var(--p1);
display:flex;align-items:center;justify-content:center;font-weight:800;font-size:13px;
flex-shrink:0;letter-spacing:.5px}
.csw a:nth-child(2) .ic{background:var(--p2bg);color:var(--p2)}
.csw .t{display:block;font-size:15.5px;font-weight:700;line-height:1.4}
.csw .s{display:block;font-size:12.5px;color:var(--muted);margin-top:3px}
.csw .cur{margin-left:auto;font-size:11px;font-weight:700;color:var(--p1);
background:var(--p1bg);border-radius:20px;padding:3px 10px;white-space:nowrap}
.dash{background:var(--card);border:1px solid var(--line);border-radius:14px;
padding:16px 18px;margin:0 0 22px}
.dhead{display:flex;align-items:baseline;gap:12px;margin-bottom:12px}
.dhead b{font-size:15px}
.dhead span{font-size:12px;color:var(--muted)}
.drow{display:flex;align-items:center;gap:12px;margin:9px 0}
.dlab{flex:0 0 42px;font-size:12.5px;font-weight:700;color:var(--muted)}
.dbar{flex:1;height:9px;background:#e8e8f2;border-radius:99px;overflow:hidden}
.dbar i{display:block;height:100%;width:0;border-radius:99px;
background:linear-gradient(90deg,#4c3a9e,#0a7d63);transition:width .25s}
.dval{flex:0 0 auto;min-width:96px;text-align:right;font-size:12.5px;font-weight:700;
font-variant-numeric:tabular-nums}
.sec-h{display:flex;align-items:baseline;gap:12px;margin:30px 0 14px}
.sec-h h2{font-size:20px;margin:0}
.sec-h span{font-size:12.5px;color:var(--muted)}
.part{display:flex;align-items:baseline;gap:10px;margin:30px 0 12px}
.part b{font-size:15.5px}
.part b::before{content:'';display:inline-block;width:4px;height:14px;background:var(--p1);
border-radius:2px;margin-right:8px;vertical-align:-1px}
.part span{font-size:12px;color:var(--muted)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(300px,100%),1fr));gap:14px}
/* 走读总览卡：一句话导语 */
.wl{font-size:12.5px;color:#4a4a63;line-height:1.7;margin:9px 0 0}
.uc{background:var(--card);border:1px solid var(--line);border-radius:14px;
padding:16px 18px 12px;display:flex;flex-direction:column}
.uc:hover{border-color:#c9c2e8}
.uc .uh{display:flex;align-items:center;gap:10px;margin-bottom:4px}
.uc .un{width:30px;height:30px;border-radius:9px;background:var(--p1);color:#fff;
display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;
flex-shrink:0}
.uc .ut{font-size:15px;font-weight:700;line-height:1.35}
.uc .um{font-size:11.5px;color:var(--muted);margin:2px 0 8px}
.uc .ul{display:flex;flex-direction:column;gap:1px;margin:2px 0 8px}
.uc .ul a{display:flex;gap:7px;font-size:12.5px;color:#3d3d55;padding:4px 6px;
border-radius:6px}
.uc .ul a:hover{background:#f4f2fd;text-decoration:none;color:var(--p1)}
.uc .ul .ln{color:var(--muted);font-size:10.5px;font-weight:700;min-width:20px;
padding-top:2px;font-variant-numeric:tabular-nums}
.uc .uf{display:flex;align-items:center;gap:8px;margin-top:auto;padding-top:10px;
border-top:1px dashed var(--line);font-size:11.5px;color:var(--muted)}
.uc .uf a{font-weight:700}
.q{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;
margin:18px 0 0}
.q a{background:var(--card);border:1px solid var(--line);border-radius:12px;
padding:13px 15px;color:inherit}
.q a:hover{border-color:var(--p1);text-decoration:none}
.q b{display:block;font-size:14px}
.q span{font-size:12px;color:var(--muted)}

/* 站内搜索 */
.hsearch{position:relative;margin:0 0 22px}
.hsearch input{width:100%;font:inherit;font-size:15px;color:var(--text);background:#fff;
border:1px solid var(--line);border-radius:12px;padding:13px 16px;
box-shadow:0 3px 14px rgba(40,30,80,.05)}
.hsearch input:focus{outline:none;border-color:var(--p1);
box-shadow:0 0 0 3px rgba(76,58,158,.12)}
.hres{position:absolute;left:0;right:0;top:calc(100% + 6px);background:#fff;
border-radius:11px;box-shadow:0 14px 38px rgba(20,20,50,.20);overflow:hidden;
display:none;max-height:420px;overflow-y:auto;z-index:30}
.hres.on{display:block}
.hres a{display:block;padding:9px 14px;border-bottom:1px solid #eef0f6;position:relative}
.hres a:last-child{border-bottom:none}
.hres a:hover,.hres a.sel{background:#f4f2fd;text-decoration:none}
.hres .t{font-size:14px;font-weight:600;color:var(--text);padding-right:52px}
.hres .s{font-size:12px;color:var(--muted);margin-top:1px}
.hres .k{position:absolute;right:12px;top:11px;font-size:10.5px;font-weight:700;
color:var(--p1);background:var(--p1bg);border-radius:4px;padding:2px 7px}
.hres .none{padding:12px 14px;font-size:13px;color:var(--muted)}
.dfoot{display:flex;align-items:center;gap:12px;margin-top:14px;padding-top:12px;
border-top:1px dashed var(--line);flex-wrap:wrap}
.rbtn{font-size:13px;font-weight:700;color:#fff;background:var(--p1);border-radius:8px;
padding:7px 14px}
.rbtn:hover{background:#3d2e86;text-decoration:none}
.mini-btn{font:inherit;font-size:12px;font-weight:600;color:var(--p1);background:#fff;
border:1px solid var(--line);border-radius:7px;padding:5px 10px;cursor:pointer}
.mini-btn:hover{background:var(--p1bg)}
.dfoot .spacer{flex:1}
.dfoot span{font-size:12.5px;color:var(--muted)}

/* 课节目录 */
.lgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(300px,100%),1fr));gap:14px}
.lu{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px}
.lu h3{margin:0 0 3px;font-size:15.5px}
.lu .m{font-size:11.5px;color:var(--muted);margin-bottom:9px}
.lu a{display:flex;gap:8px;font-size:13px;color:#3d3d55;padding:5px 6px;border-radius:6px}
.lu a:hover{background:#f4f2fd;text-decoration:none;color:var(--p1)}
.lu .ln{font-size:10.5px;font-weight:700;color:var(--muted);min-width:20px;padding-top:2px}
.lu a.done::after{content:'✓';color:var(--p2);font-weight:700;margin-left:auto}

/* 题库 */
.fbar{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0}
.fbar button{font:inherit;font-size:12.5px;font-weight:600;color:var(--muted);
background:#fff;border:1px solid var(--line);border-radius:20px;padding:5px 13px;
cursor:pointer}
.fbar button.on{color:#fff;background:var(--p1);border-color:var(--p1)}
.fbar.lvbar{align-items:center;margin-top:-6px}
.lvbar .lvlab{font-size:11.5px;color:var(--muted);letter-spacing:1px;font-weight:700;
margin-right:2px}
.lvbar button.on{background:var(--p2);border-color:var(--p2)}
.qc{background:var(--card);border:1px solid var(--line);border-radius:13px;
padding:16px 18px;margin:0 0 12px}
.qc .qh{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin-bottom:8px}
.qc .qid{font-size:11.5px;font-weight:700;color:var(--p1);background:var(--p1bg);
border-radius:5px;padding:2px 8px}
.qc .qu{font-size:11.5px;color:var(--muted)}
.qc .qt{font-size:15px;font-weight:600;line-height:1.65}
.qc .qa{margin-top:10px;display:none;border-top:1px dashed var(--line);padding-top:10px}
.qc.open .qa{display:block}
.qc .qa p:first-child{margin-top:0}
.qbtn{font:inherit;font-size:12px;font-weight:700;color:var(--p1);background:#fff;
border:1px solid var(--line);border-radius:7px;padding:4px 11px;cursor:pointer}
.qbtn:hover{background:var(--p1bg)}
.qst{display:flex;gap:6px;margin-left:auto}
.qst button{font:inherit;font-size:11.5px;font-weight:600;color:var(--muted);background:#fff;
border:1px solid var(--line);border-radius:6px;padding:3px 9px;cursor:pointer}
.qst button.on[data-s="1"]{color:#fff;background:var(--p2);border-color:var(--p2)}
.qst button.on[data-s="2"]{color:#fff;background:var(--p3);border-color:var(--p3)}
.hashnote{display:none;align-items:center;gap:10px;background:var(--p1bg);
border:1px solid #dcd5f5;border-radius:10px;padding:10px 14px;margin:0 0 12px;
font-size:13px;color:#3b3566}
.hashnote b{color:var(--p1)}
.hashnote a{margin-left:auto;font-weight:700;font-size:12.5px;white-space:nowrap}
.qempty{display:none;padding:26px 18px;text-align:center;font-size:13.5px;color:var(--muted);
background:var(--card);border:1px dashed var(--line);border-radius:12px}
.qempty{display:none;padding:26px 18px;text-align:center;font-size:13.5px;color:var(--muted);
background:var(--card);border:1px dashed var(--line);border-radius:12px}
.qc.hl{outline:2px solid var(--p3);outline-offset:2px}

/* 关卡 */
.gate{background:var(--card);border:1px solid var(--line);border-radius:14px;
padding:20px 22px;margin:0 0 18px}
.gate h2{margin:0 0 4px;font-size:19px}
.gate .gs{font-size:12.5px;color:var(--muted);margin-bottom:14px}
.gate label{display:flex;gap:10px;align-items:flex-start;padding:8px 9px;border-radius:8px;
font-size:14px;cursor:pointer;line-height:1.6}
.gate label:hover{background:#f7f6fc}
.gate input{margin-top:4px;width:17px;height:17px;accent-color:var(--p2);flex-shrink:0}
.gate label.on span{color:#0a7a5f}
.gate .gp{display:flex;align-items:center;gap:10px;margin-top:14px;
padding-top:12px;border-top:1px dashed var(--line);font-size:12.5px;color:var(--muted)}
.gate .gp b{color:var(--p1)}

/* 课件 */
.deck{position:fixed;inset:0;background:#12121c;display:flex;flex-direction:column;
z-index:0}
.slide{flex:1;display:none;padding:10vh 9vw;color:#f2f1fa;overflow-y:auto}
.slide.on{display:block}
.slide .sk{font-size:12px;font-weight:700;letter-spacing:2px;color:#a99ee0;
text-transform:uppercase;margin-bottom:16px}
.slide h2{font-size:clamp(28px,4vw,52px);line-height:1.2;margin:0 0 26px;color:#fff;
border:none;padding:0}
.slide ul{margin:0;padding-left:22px}
.slide li{font-size:clamp(15px,1.55vw,21px);line-height:1.75;margin:10px 0;color:#d8d5ea}
.slide li b{color:#fff}
.slide pre{background:#0b0b14;border:1px solid #33304a;border-radius:10px;
padding:14px 16px;margin:14px 0 10px;max-width:100%;overflow:auto;max-height:46vh}
.slide pre code{font-family:Consolas,"SFMono-Regular",monospace;
font-size:clamp(11px,1.15vw,15px);line-height:1.55;color:#d8d5ea;white-space:pre}
.slide .sub{margin-top:12px}
.slide ul li b{color:#fff}
.dnav a{color:var(--muted);text-decoration:none;font-size:12.5px;white-space:nowrap}
.dnav a:hover{color:#fff}
.slide .big{font-size:clamp(38px,6vw,78px);font-weight:800;color:#fff;line-height:1.1}
.slide .sub{font-size:clamp(15px,1.8vw,22px);color:#bdb8d8;margin-top:14px}
.dnav{position:fixed;left:0;right:0;bottom:14px;display:flex;align-items:center;
justify-content:center;gap:14px;font-size:12.5px;color:var(--muted);z-index:4}
.dnav button{font:inherit;font-size:13px;font-weight:700;color:#e8e5f7;background:#2a2840;
border:1px solid #3b3858;border-radius:8px;padding:5px 14px;cursor:pointer}
.dnav button:hover{background:#353252}
.dprog{position:fixed;left:0;top:0;height:3px;background:linear-gradient(90deg,#7c66e0,#22b98b);
width:0;z-index:5;transition:width .2s}
.dthumb{position:fixed;inset:0;background:rgba(10,10,18,.96);padding:40px;display:none;
grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px;overflow:auto;z-index:6}
.dthumb.on{display:grid}
.dthumb button{font:inherit;font-size:12px;text-align:left;color:#d8d5ea;background:#1d1c2c;
border:1px solid #33304a;border-radius:8px;padding:10px;cursor:pointer;line-height:1.45}
.dthumb button:hover{border-color:#7c66e0}
.dthumb button.cur{border-color:#22b98b;color:#fff}

@media(max-width:1000px){.lessonlist{display:block}}
@media(max-width:620px){
 .top-in{gap:8px;padding:0 12px}
 .top .tag,.top .ppt{display:none}
 .back{font-size:12px}
 .switch{font-size:12px;padding:3px 8px}
}
.tblwrap table td:first-child,.tblwrap table th:first-child{white-space:nowrap}
@media(max-width:700px){.tbl table{min-width:660px}}

.tbl{overflow-x:auto;margin-bottom:8px;border:1px solid var(--line);border-radius:12px;background:#fff}
.tbl table{width:100%;border-collapse:collapse;font-size:13px}
.tbl th,.tbl td{padding:9px 12px;text-align:left;border-bottom:1px solid #f0eff7;vertical-align:top}
.tbl th{background:#faf9fe;font-size:11.5px;letter-spacing:.5px;color:var(--muted);font-weight:700;
white-space:nowrap;position:sticky;top:0}
.tbl tr:last-child td{border-bottom:none}
.tbl td.cn{font-weight:700;color:var(--p1);font-variant-numeric:tabular-nums;width:44px}
.tbl td.sp{color:#4a4570;font-size:12.5px;max-width:280px}
.tbl td.ls,.tbl td.u{white-space:nowrap}
.tbl td.ls a{display:inline-block;margin:1px 4px 1px 0;font-size:12px;padding:2px 7px;
background:var(--p1bg);border-radius:5px;color:var(--p1);font-weight:600}
.tbl td.ls a:hover{background:#e3ddf8;text-decoration:none}
.g2box{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(300px,100%),1fr));gap:12px}
.cb{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.cb b{display:block;font-size:13.5px;margin-bottom:4px;color:#2b2545}
.cb p{margin:0;font-size:12.5px;line-height:1.75;color:#55506e}
.cx{background:#fff;border:1px solid var(--line);border-radius:12px;padding:6px 18px}
.cx p{font-size:13px;line-height:1.85;color:#4a4570;margin:10px 0}
.cx b{color:#2b2545}
.idx{columns:3;column-gap:18px}
@media(max-width:900px){.idx{columns:2}}
@media(max-width:560px){.idx{columns:1}}
.ig{break-inside:avoid;margin:0 0 14px}
.ih{font-size:11px;font-weight:800;color:var(--p1);letter-spacing:1px;border-bottom:1px solid var(--line);
padding-bottom:3px;margin-bottom:6px}
.ig ul{list-style:none;margin:0;padding:0}
.ig li{display:flex;align-items:baseline;gap:5px;font-size:12.5px;padding:2px 0;line-height:1.5}
.ig code{font-size:12px;background:#f4f2fb;border-radius:4px;padding:1px 5px;color:#3a3363;
overflow-wrap:anywhere}
.ig li a{font-size:11px;color:var(--muted);text-decoration:none;padding:0 2px;
font-variant-numeric:tabular-nums;border-bottom:1px dotted #c9c4e4}
.ig li a:hover{color:var(--p1);border-bottom-color:var(--p1)}
.ig li span{font-size:10.5px;color:#6f6a8a}
/* 实测数据页 */
.bnch{background:var(--card);border:1px solid var(--line);border-radius:14px;
padding:18px 20px;margin:0 0 14px}
.bnch .bh{margin-bottom:10px;line-height:1.6}
.bnch .bu{display:inline-block;font-size:11px;font-weight:700;color:var(--p1);
background:var(--p1bg);border-radius:5px;padding:2px 8px;margin-right:8px}
.bnch .bh b{font-size:15.5px}
.btw{overflow-x:auto;-webkit-overflow-scrolling:touch}
.bnch table{width:100%;border-collapse:collapse;font-size:13.5px;margin:4px 0 2px}
.bnch th{background:#f3f2fa;padding:8px 12px;text-align:left;font-size:12px;
color:var(--muted);border:1px solid var(--line);font-weight:600;white-space:nowrap}
.bnch td{padding:8px 12px;border:1px solid var(--line);vertical-align:top}
.bnch td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.bnch .fast{color:var(--p2)}
.bnch .bn{margin:8px 0 0;font-size:13px;line-height:1.9;color:#43435c}
.benv{background:var(--card);border:1px solid var(--line);border-radius:14px;
padding:16px 20px;margin:0 0 22px;font-size:13px;color:#3d3d55;line-height:1.9}
.benv b{color:var(--p1);margin-right:10px}
.benv span{margin-right:16px}
.benv p{margin:6px 0 0;font-size:12.5px;color:var(--muted)}
@media(max-width:620px){
 .bnch{padding:14px}
 .bnch .bh b{font-size:14px}
 .bnch td,.bnch th{padding:7px 9px;font-size:12.5px}
}

/* 复习计划（艾宾浩斯） */
.rv-sec{display:flex;align-items:baseline;gap:12px;margin:34px 0 14px}
.rv-sec h2{font-size:20px;margin:0}
.rv-sec span{font-size:12.5px;color:var(--muted)}
.rv-item{display:flex;gap:14px;background:var(--card);border:1px solid var(--line);
border-radius:13px;padding:14px 16px;margin:0 0 10px}
.rv-item.over{border-color:#ecc9c6;background:#fdf7f6}
.rv-no{flex:0 0 40px;height:40px;border-radius:10px;background:var(--p1bg);color:var(--p1);
display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:800;
font-variant-numeric:tabular-nums}
.rv-item.over .rv-no{background:var(--p4bg);color:var(--p4)}
.rv-bd{flex:1;min-width:0}
.rv-t{font-size:15px;font-weight:700;line-height:1.45}
.rv-m{font-size:12px;color:var(--muted);margin-top:2px}
.rv-m b{color:var(--p1);font-weight:700}
.rv-m .od{color:var(--p4);font-weight:700}
.rv-task{font-size:13px;color:#43435c;line-height:1.7;margin-top:6px;
background:#f7f6fc;border-radius:8px;padding:8px 12px}
.rv-act{display:flex;gap:8px;flex-wrap:wrap;margin-top:9px;align-items:center}
.rv-act a{font-size:12px;font-weight:700;color:var(--p1);background:#fff;
border:1px solid var(--line);border-radius:7px;padding:4px 11px}
.rv-act a:hover{background:var(--p1bg);text-decoration:none}
.rv-act button{font:inherit;font-size:12px;font-weight:700;color:#fff;background:var(--p2);
border:none;border-radius:7px;padding:5px 12px;cursor:pointer}
.rv-act button:hover{background:#0a7d61}
.rv-day{display:flex;align-items:baseline;gap:10px;margin:20px 0 9px}
.rv-day b{font-size:14px}
.rv-day b::before{content:'';display:inline-block;width:4px;height:13px;background:var(--p1);
border-radius:2px;margin-right:8px;vertical-align:-1px}
.rv-day span{font-size:11.5px;color:var(--muted)}
.rv-day.today b::before{background:var(--p3)}
.rv-c{display:flex;align-items:center;gap:11px;padding:8px 4px;
border-bottom:1px dashed var(--line);font-size:13px}
.rv-c:last-child{border-bottom:none}
.rv-cn{flex:0 0 26px;font-size:12px;font-weight:800;color:var(--muted);
font-variant-numeric:tabular-nums;text-align:right}
.rv-cb{flex:1;height:8px;background:#e8e8f2;border-radius:99px;overflow:hidden;min-width:40px}
.rv-cb i{display:block;height:100%;border-radius:99px;background:var(--p2)}
.rv-cb i.mid{background:var(--p3)}
.rv-cb i.low{background:var(--p4)}
.rv-cv{flex:0 0 44px;font-size:12px;font-weight:700;text-align:right;
font-variant-numeric:tabular-nums}
.rv-ct{flex:0 0 auto;font-size:12.5px;color:#3d3d55;min-width:0;overflow:hidden;
text-overflow:ellipsis;white-space:nowrap}
.rv-rule{background:var(--card);border:1px solid var(--line);border-radius:14px;
padding:20px 24px;margin-top:34px;font-size:13.5px;line-height:1.9;color:#3d3d55}
.rv-rule h3{margin:0 0 8px;font-size:15.5px;color:var(--p1)}
.rv-rule table{width:100%;border-collapse:collapse;font-size:13px;margin:10px 0}
.rv-rule th{background:#f3f2fa;padding:8px 11px;text-align:left;font-size:12.5px;
color:var(--muted);border:1px solid var(--line);font-weight:600}
.rv-rule td{padding:8px 11px;border:1px solid var(--line);vertical-align:top}
.rv-empty{background:var(--card);border:1px dashed var(--line);border-radius:13px;
padding:30px 22px;text-align:center;font-size:13.5px;color:var(--muted);line-height:1.9}
.rv-empty a{font-weight:700}
.rv-foot{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-top:26px;
font-size:12px;color:var(--muted)}
.rv-foot button{font:inherit;font-size:12px;font-weight:600;color:var(--p4);background:#fff;
border:1px solid #ecc9c6;border-radius:7px;padding:5px 11px;cursor:pointer}
.rv-foot button:hover{background:var(--p4bg)}
@media(max-width:620px){
 .rv-item{flex-direction:column;gap:9px}
 .rv-no{width:40px}
 .rv-ct{flex:1 1 auto;white-space:normal}
 .rv-c{flex-wrap:wrap}
 .rv-rule{padding:16px 16px}
 .rv-rule table{font-size:12px}
}
@media print{
 .top,.side,.pbar,.pn,#toTop,pre .cp{display:none!important}
 .layout{display:block;padding:0}
 .main{border:none;padding:0}
 .main pre{white-space:pre-wrap}
 /* 代码块两种主题都是深色底，打印出来一整页黑还费墨 → 打印翻白底深字 */
 .main pre,.wrap pre{background:#fff!important;color:#1a1a2b!important;
  border:1px solid #ccc;break-inside:avoid}
 .main pre code,.wrap pre code{color:#1a1a2b!important}
 .main pre .cl,.wrap pre .cl{color:#55687a!important;background:none!important}
}
@media(max-width:1000px){
 .layout{flex-direction:column;align-items:stretch;padding:16px 14px 60px}
 .main{order:-1}
 .side{position:static;width:100%;max-height:none}
 .main{padding:24px 18px}
 .main h1{font-size:23px}.main h2{font-size:19px}
 .hero{padding:32px 24px}
 .hero h1{font-size:27px}
 .csw{grid-template-columns:1fr}
 .pn{flex-direction:column}
 .slide{padding:8vh 7vw}
}
"""

JS = """
(function(){
  function read(k,d){try{var v=JSON.parse(localStorage.getItem(k));return v==null?d:v}catch(e){return d}}
  window.FL={read:read};

  document.querySelectorAll('pre').forEach(function(pre){
    if(pre.querySelector('.cp')) return;
    var b=document.createElement('button');
    b.className='cp';b.type='button';b.textContent='复制';
    b.addEventListener('click',function(){
      var code=pre.querySelector('code')||pre, txt=code.innerText;
      function ok(){b.textContent='已复制 ✓';b.classList.add('ok');
        setTimeout(function(){b.textContent='复制';b.classList.remove('ok')},1500);}
      function fb(){var t=document.createElement('textarea');t.value=txt;
        t.style.position='fixed';t.style.opacity='0';document.body.appendChild(t);
        t.select();try{document.execCommand('copy');ok()}catch(e){}
        document.body.removeChild(t);}
      if(navigator.clipboard&&navigator.clipboard.writeText){
        navigator.clipboard.writeText(txt).then(ok,fb);
      }else fb();
    });
    pre.appendChild(b);
  });

  var top=document.createElement('button');
  top.id='toTop';top.type='button';top.title='回到顶部';top.textContent='↑';
  document.body.appendChild(top);
  function sync(){top.classList.toggle('on',window.scrollY>500)}
  window.addEventListener('scroll',sync,{passive:true});sync();
  top.addEventListener('click',function(){window.scrollTo({top:0,behavior:'smooth'})});

  // 目录当前项高亮
  var links=[].slice.call(document.querySelectorAll('.toc a'));
  var pairs=links.map(function(a){
    var t=document.getElementById(a.getAttribute('href').slice(1));
    return t?[a,t]:null;
  }).filter(Boolean);
  function spy(){
    if(!pairs.length) return;
    var cur=pairs[0][0];
    var atBottom = window.innerHeight + window.scrollY
                   >= document.documentElement.scrollHeight - 4;
    if(atBottom){
      cur = pairs[pairs.length-1][0];
    }else{
      var y=window.scrollY+150;
      pairs.forEach(function(p){
        var top=p[1].getBoundingClientRect().top+window.scrollY;
        if(top<=y) cur=p[0];
      });
    }
    links.forEach(function(a){ a.classList.toggle('cur',a===cur); });
  }
  spy();window.addEventListener('scroll',spy,{passive:true});
})();
"""

def dedupe_ids(h):
    """同一页多次转换时，h2/h3 的 id 可能重名（每节都有「讲解」）。
    注意：源 id 本身可能已带 `-1` 后缀，要逐一看占用，不能只靠计数。"""
    used = set()

    def repl(m):
        base = m.group(1)
        cand, n = base, 1
        while cand in used:
            cand = f"{base}-{n}"
            n += 1
        used.add(cand)
        return f'id="{cand}"'

    return re.sub(r'id="([^"]+)"', repl, h)

HEAD_JS = """
window.FL = { read: function (k, d) {
  try { var v = JSON.parse(localStorage.getItem(k)); return v == null ? d : v; }
  catch (e) { return d; }
} };
"""

def page(title, body, *, where="web", unit=None, extra_head="", extra_body="",
         body_attr=""):
    """where 决定相对路径：web=flument/web/*.html，lesson=web/lessons/*.html，home=首页。"""
    if where == "home":
        css, home, switch, pre = "web/css/site.css", "index.html", "../index.html", "web/"
    elif where == "lesson":
        css, home, switch, pre = "../css/site.css", "../../index.html", "../../../index.html", "../"
    else:
        css, home, switch, pre = "css/site.css", "../index.html", "../../index.html", ""
    unit_link = (f'<a class="tag" href="{pre}{unit:02d}.html">单元 {unit}</a>'
                 if unit else "")
    ppt_link = (f'<a class="ppt" href="{pre}ppt/u/{unit:02d}.html">本单元课件</a>'
                if unit else "")
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="theme-color" content="#4c3a9e">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%234c3a9e'/%3E%3Ctext x='16' y='22' font-size='13' font-family='monospace' fill='%23fff' text-anchor='middle'%3EFP%3C/text%3E%3C/svg%3E">
<script>{HEAD_JS}</script>
<link rel="stylesheet" href="{css}">
{extra_head}
</head>
<body {body_attr}>
<div class="top"><div class="top-in">
  {'' if where == "home" else f'<a class="back" href="{home}">← 课程首页</a>'}
  <h1>{html.escape(title)}</h1>
  {unit_link}
  {ppt_link}
  <a class="switch" href="{switch}">切换课程</a>
</div></div>
{body}
{extra_body}
<script>{JS}</script>
</body>
</html>"""

def side_block(unit, lesson_no=None, toc=""):
    """单元页 / 课节页的侧栏：本单元课节 + 配套入口。"""
    links = []
    for L in unit["lessons"]:
        g = (unit["no"] - 1) * LESSONS_PER_UNIT + L["local"]
        cls = "cur" if g == lesson_no else ""
        links.append(f'<a class="{cls}" data-l="{g}" href="lessons/l{g:02d}.html">'
                     f'<span class="no">{g:02d}</span>'
                     f'<span class="tx">{html.escape(L["title"])}</span></a>')
    lo = (unit["no"] - 1) * LESSONS_PER_UNIT + 1
    hi = lo + LESSONS_PER_UNIT - 1
    # 本单元对应的设计取舍章节（chapters.json 的映射）
    _chs = [c for c in DESIGN_META if c["unit"] == unit["no"]]
    _ch_link = ""
    if _chs:
        _ch_link = (f'  <a href="ch/{_chs[0]["ch"]:02d}.html"><span class="k">设计</span>'
                    f'    <span class="v">设计取舍 · 第 {_chs[0]["ch"]}–{_chs[-1]["ch"]} 章</span></a>\n')
    return f"""<div class="sblk">
  <h4>本单元课节（{len(unit["lessons"])} 节）</h4>
  <div class="nlist">{''.join(links)}</div>
  <div class="mini"><i id="sideBar"></i></div>
  <div class="minitxt" id="sideTxt">已学 0 / {hi - lo + 1} 节</div>
</div>
{('<div class="sblk"><h4>本页目录</h4><div class="toc">' + toc + '</div></div>') if toc else ''}
<div class="sblk rel">
  <h4>配套入口</h4>
  <a href="bank.html#u{unit['no']}"><span class="k">题库</span>
    <span class="v">本单元 {BANK_PER_UNIT.get(unit['no'], 0)} 题 · 全站 {BANK_N} 题</span></a>
  <a href="gates.html"><span class="k">关卡</span>
    <span class="v">阶段验收清单</span></a>
  <a href="ppt/u/{unit['no']:02d}.html"><span class="k">课件</span>
    <span class="v">本单元逐节课件 · 10 页</span></a>
  <a href="ppt/index.html"><span class="k">大纲</span>
    <span class="v">18 页课程总览</span></a>
  <a href="review.html"><span class="k">复习</span>
    <span class="v">艾宾浩斯复习计划 · 6 轮</span></a>
  <a href="syllabus.html"><span class="k">课表</span>
    <span class="v">{SYL_TXT}</span></a>
  <a href="bench.html"><span class="k">实测</span>
    <span class="v">写法快慢对比 · 本机实跑</span></a>
  <a href="walk/u{unit['no']:02d}.html"><span class="k">走读</span>
    <span class="v">单元 {unit['no']} 完整程序 · 逐段讲解</span></a>
{_ch_link}</div>"""

SIDE_PROGRESS_JS = """
<script>
(function(){
  var links=[].slice.call(document.querySelectorAll('.nlist a'));
  var uniq=[], seen={};
  links.forEach(function(a){
    if(!seen[a.dataset.l]){seen[a.dataset.l]=1;uniq.push(a.dataset.l);}
  });
  var bar=document.getElementById('sideBar'), txt=document.getElementById('sideTxt');
  function paint(){
    var o=FL.read('fl-lesson-v1',{}), n=0;
    links.forEach(function(a){a.classList.toggle('done',!!o[a.dataset.l]);});
    uniq.forEach(function(k){if(o[k])n++;});
    if(bar)bar.style.width=(n/uniq.length*100)+'%';
    if(txt)txt.textContent='已学 '+n+' / '+uniq.length+' 节';
  }
  paint();window.addEventListener('focus',paint);
  document.addEventListener('visibilitychange',paint);
})();
</script>"""

# ────────────────────────────── 单元页 ──────────────────────────────

def build_units(units):
    for u in units:
        no = u["no"]
        body_html = md2html(u["intro"])
        # 课节导航卡
        cards = []
        for L in u["lessons"]:
            g = (no - 1) * LESSONS_PER_UNIT + L["local"]
            cards.append(f'<a data-l="{g}" href="lessons/l{g:02d}.html"><span class="no">{g:02d}</span>'
                         f'<span class="tx">{html.escape(L["title"])}</span></a>')
        body_html += ('<div class="lessonlist"><h4>本单元四节课</h4>'
                      '<div class="nlist">' + "".join(cards) + '</div></div>')
        for L in u["lessons"]:
            g = (no - 1) * LESSONS_PER_UNIT + L["local"]
            body_html += f'<h2 id="l{g:02d}">第 {g} 课 · {html.escape(L["title"])}</h2>'
            body_html += md2html(L["md"])
            body_html += book_box(g, L)
        body_html += md2html(u["outro"])
        body_html = dedupe_ids(body_html)

        toc = toc_h2(body_html)
        chap, wk, kw = UNIT_META[no]
        prev = (f'<a href="{(no - 1):02d}.html"><small>← 上一单元</small>'
                f'<b>单元 {no-1} · {html.escape(units[no-2]["title"])}</b></a>') if no > 1 else ""
        nxt = (f'<a class="nx" href="{(no + 1):02d}.html"><small>下一单元 →</small>'
               f'<b>单元 {no+1} · {html.escape(units[no]["title"])}</b></a>') if no < len(units) else ""

        body = f"""<div class="layout">
  <aside class="side">{side_block(u, toc=toc)}</aside>
  <main class="main">
    <div class="head">
      <div class="kicker"><span class="kno">单元 {no}</span>
        <span class="kwk">{chap}</span><span class="ku">建议 {wk}</span></div>
      <h1>单元 {no} · {html.escape(u['title'])}</h1>
      <p class="goal">{html.escape(kw)}</p>
    </div>
    <div class="goalbox"><b>完成标准：</b>本单元四节课的验收清单全部打勾，
    并完成题库中对应 3 道题，才算过关。<br>
    每节末尾的「原书对照」标出对应小节与课上未展开的细节。</div>
    {body_html}
    <div class="pn">{prev or '<span></span>'}{nxt or '<span></span>'}</div>
    <p style="font-size:12px;color:var(--muted);margin-top:14px">
      本页内容依据《流畅的 Python（第 2 版）》{chap}的章节结构课程化重写，
      示例按 Python 3.10+ 语法编写，3.11+ 特性在正文单独标注。</p>
  </main>
</div>"""
        out = page(f"单元 {no} · {u['title']}", body, unit=no,
                   extra_body=SIDE_PROGRESS_JS)
        open(os.path.join(WEB, f"{no:02d}.html"), "w", encoding="utf-8").write(out)

# ────────────────────────────── 课节页 ──────────────────────────────

def build_lessons(units):
    os.makedirs(os.path.join(WEB, "lessons"), exist_ok=True)
    flat = []
    for u in units:
        for L in u["lessons"]:
            g = (u["no"] - 1) * LESSONS_PER_UNIT + L["local"]
            flat.append((g, u, L))
    total = len(flat)

    for i, (g, u, L) in enumerate(flat):
        body_html = md2html(L["md"]) + book_box(g, L)
        toc = bl.toc_from_html(body_html)
        prev = nxt = ""
        if i > 0:
            pg, pu, pl = flat[i - 1]
            prev = (f'<a href="l{pg:02d}.html"><small>← 第 {pg} 课 · 单元 {pu["no"]}</small>'
                    f'<b>{html.escape(pl["title"])}</b></a>')
        if i < total - 1:
            ng, nu, nl = flat[i + 1]
            nxt = (f'<a class="nx" href="l{ng:02d}.html"><small>第 {ng} 课 · 单元 {nu["no"]} →</small>'
                   f'<b>{html.escape(nl["title"])}</b></a>')

        _uch = [c for c in DESIGN_META if c["unit"] == u["no"]]
        _dch = _uch[0]["ch"] if _uch else 1
        _dch2 = _uch[-1]["ch"] if _uch else 1
        rel_side = f"""<div class="sblk">
  <h4>本单元课节（{len(u['lessons'])} 节）</h4>
  <div class="nlist">{''.join(
      f'<a class="{"cur" if x["local"] == L["local"] else ""}" data-l="{(u["no"]-1)*LESSONS_PER_UNIT + x["local"]}" '
      f'href="l{(u["no"]-1)*LESSONS_PER_UNIT + x["local"]:02d}.html">'
      f'<span class="no">{(u["no"]-1)*LESSONS_PER_UNIT + x["local"]:02d}</span>'
      f'<span class="tx">{html.escape(x["title"])}</span></a>' for x in u["lessons"])}</div>
</div>
<div class="sblk">
  <h4>本页目录</h4>
  <div class="toc">{toc}</div>
</div>
<div class="sblk rel">
  <h4>配套入口</h4>
  <a href="../{u['no']:02d}.html"><span class="k">单元</span>
    <span class="v">单元 {u['no']} · {html.escape(u['title'])}</span></a>
  <a href="../bank.html#u{u['no']}"><span class="k">题库</span>
    <span class="v">本单元 3 题</span></a>
  <a href="../gates.html"><span class="k">关卡</span>
    <span class="v">阶段验收</span></a>
  <a href="../ppt/u/{u['no']:02d}.html#s{2 * L['local']}"><span class="k">课件</span>
    <span class="v">本单元第 {L['local']} 课 · 2 页</span></a>
  <a href="../review.html"><span class="k">复习</span>
    <span class="v">艾宾浩斯复习计划 · 6 轮</span></a>
  <a href="../bench.html"><span class="k">实测</span>
    <span class="v">写法快慢对比 · 本机实跑</span></a>
  <a href="../walk/u{u['no']:02d}.html"><span class="k">走读</span>
    <span class="v">本单元完整程序 · 逐段讲解</span></a>
  <a href="../ch/{_dch:02d}.html"><span class="k">设计</span>
    <span class="v">设计取舍 · 第 {_dch}–{_dch2} 章</span></a>
</div>"""

        body = f"""<div class="pbar"><i style="width:{g / total * 100:.1f}%"></i></div>
<div class="layout">
  <aside class="side">{rel_side}</aside>
  <main class="main">
    <div class="head">
      <div class="kicker">
        <span class="kno">第 {g} 课</span>
        <span class="kwk">单元 {u['no']} · {UNIT_META[u['no']][0]}</span>
        <span class="ku">90 分钟</span>
      </div>
      <h1>{html.escape(L['title'])}</h1>
    </div>
    {f'<div class="goalbox"><b>本节目标：</b>{html.escape(L["goal"])}</div>' if L["goal"] else ''}
    {body_html}
    <div class="pn">{prev or '<span></span>'}{nxt or '<span></span>'}</div>
    <div style="margin-top:22px;display:flex;align-items:center;gap:14px;flex-wrap:wrap">
      <label class="mark"><input type="checkbox" id="doneBox"><span>标记本课已学完</span></label>
      <span style="font-size:12px;color:var(--muted)">完成后自动写入本机进度（不联网）</span>
      <a style="margin-left:auto;font-size:12.5px;font-weight:700"
         href="../{u['no']:02d}.html">返回单元 {u['no']}</a>
    </div>
  </main>
</div>"""
        js = """<script>
(function(){
  var g=__G__, box=document.getElementById('doneBox'), lab=box.closest('.mark');
  var KEY='fl-lesson-v1';
  var o=FL.read(KEY,{});
  // 迁移：旧版只存 1，没有完成时间；复习排程需要时间戳
  var moved=false;
  for(var k in o){ if(o[k]===1){ o[k]=Date.now(); moved=true; } }
  if(moved){ try{localStorage.setItem(KEY,JSON.stringify(o))}catch(e){} }
  box.checked=!!o[g]; lab.classList.toggle('on',box.checked);
  box.addEventListener('change',function(){
    var m=FL.read(KEY,{});
    if(box.checked)m[g]=Date.now(); else delete m[g];
    try{localStorage.setItem(KEY,JSON.stringify(m))}catch(e){}
    lab.classList.toggle('on',box.checked);
  });
})();
</script>""".replace("__G__", str(g))
        out = page(f"第 {g} 课 · {L['title']}", body, where="lesson", unit=u["no"],
                   body_attr=f'data-g="{g}"', extra_body=js + SIDE_PROGRESS_JS)
        open(os.path.join(WEB, "lessons", f"l{g:02d}.html"), "w",
             encoding="utf-8").write(out)

    # 课节目录
    blocks = []
    for u in units:
        rows = []
        for L in u["lessons"]:
            g = (u["no"] - 1) * LESSONS_PER_UNIT + L["local"]
            rows.append(f'<a data-l="{g}" href="l{g:02d}.html"><span class="ln">{g:02d}</span>'
                        f'{html.escape(L["title"])}</a>')
        blocks.append(f"""<div class="lu">
  <h3>单元 {u['no']} · {html.escape(u['title'])}</h3>
  <div class="m">{UNIT_META[u['no']][0]} ｜ 建议 {UNIT_META[u['no']][1]}</div>
  {''.join(rows)}</div>""")

    body = f"""<div class="wrap">
  <div class="hero" style="padding:38px 40px">
    <div class="bdg">COURSE MAP</div>
    <h1>48 节课 · 一课 90 分钟</h1>
    <p>按「机制精讲 → 惯用法 → 实战改造 → 坑与验收」四步推进。每节课都能单独打开，
    顶部可切回单元、题库或关卡。</p>
  </div>
  <div class="dash">
    <div class="dhead"><b>整体进度</b><span id="pgTxt">已学 0 / 48 节</span></div>
    <div class="dbar"><i id="pgBar"></i></div>
  </div>
  <div class="lgrid">{''.join(blocks)}</div>
</div>
<script>
(function(){{
  function paint(){{
    var o=FL.read('fl-lesson-v1',{{}}),n=0;
    document.querySelectorAll('.lu a').forEach(function(a){{
      var d=!!o[a.dataset.l];a.classList.toggle('done',d);if(d)n++;}});
    document.getElementById('pgBar').style.width=(n/48*100)+'%';
    document.getElementById('pgTxt').textContent='已学 '+n+' / 48 节';
  }}
  paint();window.addEventListener('focus',paint);
  document.addEventListener('visibilitychange',paint);
}})();
</script>"""
    out = page("课程目录 · 48 节课", body, where="lesson")
    open(os.path.join(WEB, "lessons", "index.html"), "w", encoding="utf-8").write(out)

# ────────────────────────────── 题库 ──────────────────────────────

def build_bank(units):
    data = json.load(open(os.path.join(SRC, "bank.json"), encoding="utf-8"))
    if len(data) != BANK_N:
        raise SystemExit(f"题库应有 {BANK_N} 题，实际 {len(data)} 题")
    for u in units:
        n = sum(1 for q in data if q["unit"] == u["no"])
        if n < 3:
            raise SystemExit(f"单元 {u['no']} 只有 {n} 题，每单元至少 3 题")
    cards = []
    for q in data:
        u = q["unit"]
        st = f'{q["level"]} · 单元 {u}'
        cards.append(f"""<div class="qc" id="{q['id']}" data-u="{u}" data-lv="{html.escape(q['level'])}">
  <div class="qh"><span class="qid">{q['id']}</span><span class="qu">{st}</span>
    <div class="qst"><button data-s="1">已掌握</button><button data-s="2">待复习</button></div>
  </div>
  <div class="qt">{md2html(q['q'])}</div>
  <button class="qbtn">显示答案</button>
  <div class="qa">{md2html(q['a'])}</div>
</div>""")

    body = f"""<div class="wrap">
  <div class="hero" style="padding:38px 40px">
    <div class="bdg">BANK</div>
    <h1>{BANK_N} 题 · 从「看懂」到「写得出」</h1>
    <p>每个单元 {BANK_PER_UNIT[1]} 题：机制 / 代码 / 设计各一，另有一道进阶题。先自己写，再展开答案对照；
    标记「待复习」的题可以单独筛出来集中二刷。</p>
  </div>
  <div class="fbar" id="fb">
    <button class="on" data-k="all">全部 {BANK_N}</button>
    <button data-k="todo">待复习</button>
    <button data-k="master">已掌握</button>
    <button data-k="u1">单元 1–3</button>
    <button data-k="u2">单元 4–6</button>
    <button data-k="u3">单元 7–9</button>
    <button data-k="u4">单元 10–12</button>
  </div>
  <div class="fbar lvbar" id="lvb">
    <span class="lvlab">按档位</span>
    <button class="on" data-lv="">不分档</button>
    <button data-lv="概念">概念 12</button>
    <button data-lv="代码">代码 12</button>
    <button data-lv="设计">设计 12</button>
  </div>
  <div class="hashnote" id="hn"><b id="hnT"></b><a href="bank.html">查看全部 {BANK_N} 题</a></div>
  <div id="list">{''.join(cards)}</div>
  <p class="qempty" id="qempty">没有符合条件的题目</p>
</div>
<script>
(function(){{
  var st=FL.read('fl-bank-v1',{{}});
  document.querySelectorAll('.qc').forEach(function(c){{
    c.querySelector('.qbtn').addEventListener('click',function(){{
      c.classList.toggle('open');
      this.textContent=c.classList.contains('open')?'收起答案':'显示答案';
    }});
  }});
  function paintState(){{
    document.querySelectorAll('.qc').forEach(function(c){{
      var id=c.querySelector('.qid').textContent, v=st[id];
      c.querySelectorAll('.qst button').forEach(function(b){{
        b.classList.toggle('on',String(v)===b.dataset.s);}});
    }});
  }}
  document.querySelectorAll('.qst button').forEach(function(b){{
    b.addEventListener('click',function(){{
      var c=b.closest('.qc'), id=c.querySelector('.qid').textContent;
      if(st[id]===+b.dataset.s) delete st[id]; else st[id]=+b.dataset.s;
      try{{localStorage.setItem('fl-bank-v1',JSON.stringify(st))}}catch(e){{}}
      paintState();
    }});
  }});
  paintState();
  var fb=document.getElementById('fb'), lvb=document.getElementById('lvb');
  var k='all', lv='';
  function applyFilter(){{
    var hn=document.getElementById('hn'); if(hn) hn.style.display='none';
    var vis=0;
    document.querySelectorAll('.qc').forEach(function(c){{
      var id=c.querySelector('.qid').textContent, u=+c.dataset.u, show=true;
      if(k==='todo') show=st[id]===2;
      else if(k==='master') show=st[id]===1;
      else if(k==='u1') show=u<=3;
      else if(k==='u2') show=u>=4&&u<=6;
      else if(k==='u3') show=u>=7&&u<=9;
      else if(k==='u4') show=u>=10;
      if(lv && c.dataset.lv!==lv) show=false;
      c.style.display=show?'':'none';
      if(show) vis++;
    }});
    document.getElementById('qempty').style.display=vis?'none':'block';
  }}
  fb.addEventListener('click',function(e){{
    var b=e.target.closest('button'); if(!b) return;
    fb.querySelectorAll('button').forEach(function(x){{x.classList.toggle('on',x===b)}});
    k=b.dataset.k; applyFilter();
  }});
  lvb.addEventListener('click',function(e){{
    var b=e.target.closest('button'); if(!b) return;
    lvb.querySelectorAll('button').forEach(function(x){{x.classList.toggle('on',x===b)}});
    lv=b.dataset.lv; applyFilter();
  }});
  window.BANK_FILTER=function(kk){{                       // #review 深链用
    var b=fb.querySelector('button[data-k="'+kk+'"]');
    if(b) b.click();
  }};
}})();
</script>"""
    bank_js = """
<script>
(function(){
  var all = [].slice.call(document.querySelectorAll('.qc'));
  function unit(n){
    all.forEach(function(c){ c.style.display = (+c.dataset.u === n) ? '' : 'none'; });
    var note = document.getElementById('hn');
    note.style.display = 'flex';
    document.querySelectorAll('#fb button').forEach(function(b){ b.classList.remove('on'); });
    document.getElementById('hnT').textContent = '只看单元 ' + n + ' 的 3 道题';
    window.scrollTo({top: 0, behavior: 'smooth'});
  }
  function apply(){
    var h = location.hash || '';
    var m = h.match(/^#u(\\d+)$/);
    if (m) { unit(+m[1]); return; }
    if (h === '#review') { if (window.BANK_FILTER) window.BANK_FILTER('todo'); return; }
    document.getElementById('hn').style.display = 'none';
    document.getElementById('qempty').style.display = 'none';
    all.forEach(function(c){ c.style.display = ''; });
    if (/^#F\\d+-\\d+$/.test(h)) {
      var el = document.getElementById(h.slice(1));
      if (el) {
        el.classList.add('hl');
        el.scrollIntoView({block: 'center'});
        setTimeout(function(){ el.classList.remove('hl'); }, 2200);
      }
    }
  }
  window.addEventListener('hashchange', apply);
  apply();
})();
</script>"""
    out = page(f"题库 · {BANK_N} 题", body + bank_js, where="web")
    open(os.path.join(WEB, "bank.html"), "w", encoding="utf-8").write(out)

# ────────────────────────────── 关卡 ──────────────────────────────

def build_gates(units):
    def block(title, sub, items, key, no):
        rows = "".join(
            f'<label><input type="checkbox" data-g="{key}" data-i="{i}">'
            f'<span>{html.escape(t)}</span></label>' for i, (_u, t) in enumerate(items))
        return f"""<div class="gate" data-key="{key}">
  <h2>{title}</h2><div class="gs">{sub}</div>
  {rows}
  <div class="gp"><b id="n_{key}">0 / {len(items)}</b>
    <div class="dbar" style="flex:1"><i id="b_{key}"></i></div>
    <a href="../index.html#units">回到单元首页</a></div>
</div>"""

    body = f"""<div class="wrap">
  <div class="hero" style="padding:38px 40px">
    <div class="bdg">GATES</div>
    <h1>两个关卡 · 判定「真的会了」</h1>
    <p>关卡不是考试，是验收：每条都必须能当场演示或讲清楚。做完勾选，进度存在本机。</p>
  </div>
  {block("关卡 1 · 数据结构、函数与对象", "覆盖单元 1–6 ｜ 建议在第 12 周完成后验收", GATE1, "g1", 1)}
  {block("关卡 2 · 类、并发与元编程", "覆盖单元 7–12 ｜ 建议在第 24 周完成后验收", GATE2, "g2", 2)}
</div>
<script>
(function(){{
  ['g1','g2'].forEach(function(k){{
    var box=document.querySelector('.gate[data-key="'+k+'"]');
    var st=FL.read('fl-gate'+k.slice(1)+'-v1',{{}});
    var ins=[].slice.call(box.querySelectorAll('input'));
    function paint(){{
      var n=0;ins.forEach(function(x){{x.closest('label').classList.toggle('on',x.checked);
        if(x.checked)n++;}});
      document.getElementById('n_'+k).textContent=n+' / '+ins.length;
      document.getElementById('b_'+k).style.width=(n/ins.length*100)+'%';
    }}
    ins.forEach(function(x){{x.checked=!!st[x.dataset.i];
      x.addEventListener('change',function(){{
        if(x.checked)st[x.dataset.i]=1; else delete st[x.dataset.i];
        try{{localStorage.setItem('fl-gate'+k.slice(1)+'-v1',JSON.stringify(st))}}catch(e){{}}
        paint();
      }})}});
    paint();
  }});
}})();
</script>"""
    out = page("关卡验收", body, where="web")
    open(os.path.join(WEB, "gates.html"), "w", encoding="utf-8").write(out)

# ────────────────────────────── 课件 ──────────────────────────────

SLIDES = [
    ("Fluent Python · 2nd Edition", "把「能跑」写成「像 Python」", [
        "24 章拆成 12 个单元、48 节课", "每节课 90 分钟：讲机制、改代码、做验收",
        "先修：能写函数与类，用过 pip 和虚拟环境"]),
    ("怎么上这门课", "四段式课节结构", [
        "机制精讲 30 分钟：为什么这样设计", "惯用法 20 分钟：标准库怎么写",
        "实战改造 30 分钟：把普通代码重构成 Pythonic", "验收 10 分钟：清单逐条过"]),
    ("教材坐标", "5 部分 · 24 章 → 12 单元", [
        "第一部分 数据结构（1–6 章）", "第二部分 函数即对象（7–10 章）",
        "第三部分 类和协议（11–16 章）", "第四部分 控制流（17–21 章）",
        "第五部分 元编程（22–24 章）"]),
    ("学习者画像", "这门课适合谁", [
        "写过 1000 行以上 Python，但代码像 Java/JS",
        "能看懂别人的库，自己设计类时没把握", "准备读框架源码、写中间件或做代码评审"]),
    ("单元 1–3", "数据与对象：先把地基换成 Python 的", [
        "特殊方法是语言协议的入口，不是语法糖",
        "dict 的顺序与性能都由哈希表决定",
        "别名、可变性与 Unicode 是 bug 的高发区"]),
    ("单元 4–5", "函数：从「能调用」到「能组合」", [
        "函数是一等对象，可以传、可以返回、可以存",
        "类型提示是给工具看的文档，不是运行时检查",
        "闭包捕获的是变量，不是值"]),
    ("单元 6–8", "类与协议：写出可组合的类型", [
        "先有协议，再有继承；鸭子类型优先",
        "ABC 负责「明确契约」，Protocol 负责「结构化匹配」",
        "运算符重载必须保持交换律与一致性"]),
    ("单元 9", "控制流：惰性与上下文", [
        "生成器把「计算」变成「按需产出」", "yield from 是委派，不是简写",
        "with 管理资源，match 解构数据"]),
    ("单元 10–11", "并发与异步：先判断瓶颈", [
        "CPU 密集 → 进程；IO 密集 → 线程或协程",
        "GIL 保护解释器状态，不等于线程安全",
        "asyncio 的收益来自「等待时不占线程」"]),
    ("单元 12", "元编程：把重复交给机制", [
        "__getattr__ 处理「运行时才知道的属性」",
        "描述符把「属性访问」变成可复用的逻辑",
        "元类只在类创建时介入，优先用 __init_subclass__"]),
    ("每节课的产出", "不是笔记，是可运行的代码", [
        "一段能跑的最小示例", "一次「错误写法 → 正确写法」的对照",
        "一张验收清单，勾完才算学完"]),
    ("代码标准", "按团队代码的标准要求自己", [
        "公开函数写全类型注解，mypy 无报错",
        "异常只捕获能处理的类型，不写裸 except",
        "复杂分支用数据驱动或模式匹配，不堆 if"]),
    ("题库设计", f"{BANK_N} 题：机制 / 代码 / 设计", [
        "机制题：解释「为什么」", "代码题：手写可运行片段",
        "设计题：给定需求选型并说明理由"]),
    ("两个关卡", "验收而不是考试", [
        "关卡 1（第 12 周）：数据结构、函数、对象",
        "关卡 2（第 24 周）：类、并发、元编程",
        "每条都能当场演示或讲清楚，才算过关"]),
    ("时间预算", "24 周 · 每周 2 节课", [
        "每节课 90 分钟，课后 1–2 小时代码量",
        "48 节正好 24 周；元编程可以放慢，但别跳过描述符",
        "进度落后时先砍练习题，不砍验收"]),
    ("常见卡点", "大多数人会卡在这五处", [
        "把特殊方法当普通方法直接调用",
        "以为 dict 有序就等于可以排序",
        "装饰器丢了 functools.wraps",
        "以为多线程能加速 CPU 密集任务",
        "描述符与 __getattr__ 的优先级搞混"]),
    ("验收标准", "学完能做到什么", [
        "为一个真实需求设计出 3 层以内的类结构",
        "读懂 80% 的标准库与框架源码",
        "写出同事愿意 review、而不是绕开的代码"]),
    ("结束", "接下来做什么", [
        "挑一个你常用的库，读它的核心模块",
        "把工作里的一个模块按本课标准重构",
        "回到题库，把「待复习」清零"]),
]

def build_deck(units):
    slides = []
    for i, (kick, title, items) in enumerate(SLIDES, 1):
        lis = "".join(f"<li>{html.escape(x)}</li>" for x in items)
        slides.append(f"""<section class="slide{' on' if i == 1 else ''}" data-s="{i}">
  <div class="sk">{html.escape(kick)}</div>
  <h2>{html.escape(title)}</h2>
  <ul>{lis}</ul>
</section>""")
    thumbs = "".join(
        f'<button data-s="{i}"><b>{i:02d}</b> · {html.escape(s[1])}</button>'
        for i, s in enumerate(SLIDES, 1))
    body = f"""<div class="deck">{''.join(slides)}</div>
<div class="dprog" id="dp"></div>
<div class="dthumb" id="dt">{thumbs}</div>
<div class="dnav">
  <button id="prev">←</button><span id="cnt">1 / {len(SLIDES)}</span>
  <button id="next">→</button>
  <button id="ov">目录</button>
</div>"""
    extra = """<script>
(function(){
  var cur=1, n=__N__, slides=[].slice.call(document.querySelectorAll('.slide'));
  var dp=document.getElementById('dp'), cnt=document.getElementById('cnt'),
      dt=document.getElementById('dt');
  function go(i){
    cur=Math.max(1,Math.min(n,i));
    slides.forEach(function(s){s.classList.toggle('on',+s.dataset.s===cur)});
    dp.style.width=(cur/n*100)+'%';
    cnt.textContent=cur+' / '+n;
    if(location.hash!=='#s'+cur){try{history.replaceState(null,'','#s'+cur)}catch(e){}}
  }
  document.getElementById('prev').onclick=function(){go(cur-1)};
  document.getElementById('next').onclick=function(){go(cur+1)};
  document.getElementById('ov').onclick=function(){dt.classList.toggle('on')};
  dt.addEventListener('click',function(e){
    var b=e.target.closest('button'); if(!b)return;
    go(+b.dataset.s);dt.classList.remove('on');
  });
  document.addEventListener('keydown',function(e){
    if(e.key==='ArrowRight'||e.key===' '||e.key==='PageDown'){e.preventDefault();go(cur+1)}
    if(e.key==='ArrowLeft'||e.key==='PageUp'){e.preventDefault();go(cur-1)}
    if(e.key==='Escape'){dt.classList.remove('on')}
    if(e.key==='o'||e.key==='O'){dt.classList.toggle('on')}
  });
  var m=(location.hash||'').match(/^#s(\\d+)$/);
  go(m?+m[1]:1);
  var x0=null;
  document.addEventListener('touchstart',function(e){x0=e.touches[0].clientX},{passive:true});
  document.addEventListener('touchend',function(e){
    if(x0===null)return;
    var dx=e.changedTouches[0].clientX-x0;
    if(Math.abs(dx)>50) go(cur+(dx<0?1:-1));
    x0=null;
  },{passive:true});
})();
</script>""".replace("__N__", str(len(SLIDES)))
    out = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>大纲课件 · 18 页</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%234c3a9e'/%3E%3Ctext x='16' y='22' font-size='13' font-family='monospace' fill='%23fff' text-anchor='middle'%3EFP%3C/text%3E%3C/svg%3E">
<link rel="stylesheet" href="../css/site.css">
</head><body>
{body}
<div style="position:fixed;left:14px;top:12px;z-index:7">
  <a href="../../index.html" style="color:var(--muted);font-size:12.5px">← 课程首页</a>
  <span style="color:var(--muted)">·</span>
  <a href="u/index.html" style="color:var(--muted);font-size:12.5px">逐节课件</a>
</div>
{extra}
</body></html>"""
    out = out.replace("18 页", f"{len(SLIDES)} 页")
    os.makedirs(os.path.join(WEB, "ppt"), exist_ok=True)
    open(os.path.join(WEB, "ppt", "index.html"), "w", encoding="utf-8").write(out)

# ────────────────────────────── 首页 ──────────────────────────────

HOME_JS = """
var IDX = __IDX__, LESSONS = __LESSONS__;
var L = FL.read('fl-lesson-v1', {}), B = FL.read('fl-bank-v1', {});
var ln = Object.keys(L).length, bn = 0;
for (var k in B) if (B[k] === 1) bn++;

function set(id, txt, bar, p, total) {
  document.getElementById(id).textContent = txt;
  document.getElementById(bar).style.width = (p / total * 100) + '%';
}
set('tL', '已学 ' + ln + ' / 48', 'pL', ln, 48);
set('tB', '掌握 ' + bn + ' / __BANKN__', 'pB', bn, __BANKN__);

var un = 0;
for (var u = 1; u <= 12; u++) {
  var n = 0;
  for (var i = (u - 1) * 4 + 1; i <= u * 4; i++) if (L[i]) n++;
  var el = document.querySelector('[data-prog="u' + u + '"]');
  if (el) el.textContent = '已学 ' + n + ' / 4';
  if (n === 4) un++;
}
set('tU', '完成 ' + un + ' / 12', 'pU', un, 12);

var first = null;
for (var j = 0; j < LESSONS.length; j++) {
  if (!L[LESSONS[j].n]) { first = LESSONS[j]; break; }
}
var rl = document.getElementById('rlink'), rt = document.getElementById('rtxt');
if (first) {
  rl.href = 'web/lessons/l' + String(first.n).padStart(2, '0') + '.html';
  rl.textContent = (ln === 0 ? '开始第 ' : '继续第 ') + first.n + ' 课';
  rt.textContent = first.t;
} else {
  rl.href = 'web/bank.html';
  rl.textContent = '48 节全部完成';
  rt.textContent = '去题库把「待复习」清零';
}

// 今日复习（与 web/review.html 同一套艾宾浩斯间隔）
(function(){
  var STAGES = [0, 1, 3, 7, 15, 30], DAY = 86400000;
  var R = FL.read('fl-review-v1', {});
  function mid(t){ var d = new Date(t); d.setHours(0,0,0,0); return d.getTime(); }
  var today = mid(Date.now()), due = 0, later = 0;
  for (var k in L) {
    var learned = mid(L[k] === 1 ? Date.now() : L[k]);
    var rs = R[k] || [];
    for (var i = 0; i < STAGES.length; i++) {
      if (rs[i]) continue;
      if (learned + STAGES[i] * DAY <= today) due++; else later++;
    }
  }
  document.getElementById('rvT').textContent = due + ' 项';
  document.getElementById('rvP').style.width = Math.min(100, due * 10) + '%';
  var txt = document.getElementById('rvTxt');
  if (!ln) txt.textContent = '学完一节课，当天就会自动排第一轮';
  else if (due) txt.textContent = '今天到期 ' + due + ' 项，未来还有 ' + later + ' 项';
  else txt.textContent = '今天没有到期项，未来共 ' + later + ' 项';
})();

var KEYS = ['fl-lesson-v1', 'fl-bank-v1', 'fl-gate1-v1', 'fl-gate2-v1', 'fl-review-v1'];
document.getElementById('expBtn').addEventListener('click', function () {
  var data = { v: 1, at: new Date().toISOString() };
  KEYS.forEach(function (k) {
    var raw = localStorage.getItem(k);
    if (raw) { try { data[k] = JSON.parse(raw); } catch (e) {} }
  });
  var blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'fluent-python-progress.json';
  a.click();
  setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
});
document.getElementById('impBtn').addEventListener('click', function () {
  document.getElementById('impFile').click();
});
document.getElementById('impFile').addEventListener('change', function () {
  var f = this.files && this.files[0];
  if (!f) return;
  var r = new FileReader();
  r.onload = function () {
    try {
      var d = JSON.parse(r.result);
      KEYS.forEach(function (k) {
        if (d && d[k]) localStorage.setItem(k, JSON.stringify(d[k]));
      });
      location.reload();
    } catch (e) {
      alert('文件格式不正确，请选择本课程导出的 JSON。');
    }
  };
  r.readAsText(f);
});

var input = document.getElementById('fs'), res = document.getElementById('fsRes');
function esc(s) {
  return s.replace(/[&<>"]/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
  });
}
function run() {
  var q = input.value.trim().toLowerCase();
  if (!q) { res.classList.remove('on'); res.innerHTML = ''; return; }
  var hits = [], seen = {};
  for (var i = 0; i < IDX.length; i++) {
    var x = IDX[i];
    var inT = x.t.toLowerCase().indexOf(q) >= 0;
    var inW = (x.w || '').toLowerCase().indexOf(q) >= 0;
    var inS = x.s.toLowerCase().indexOf(q) >= 0;
    if ((inT || inW || inS) && !seen[x.u]) {
      seen[x.u] = 1;
      hits.push({ x: x, score: (inT ? 4 : 0) + (inW ? 2 : 0) + (inS ? 1 : 0) });
    }
  }
  hits.sort(function (a, b) { return b.score - a.score; });
  hits = hits.slice(0, 10).map(function (h) { return h.x; });
  res.innerHTML = hits.length
    ? hits.map(function (x) {
        return '<a href="' + x.u + '"><span class="k">' + x.k + '</span>' +
               '<div class="t">' + esc(x.t) + '</div>' +
               '<div class="s">' + esc(x.s) + '</div></a>';
      }).join('')
    : '<div class="none">没有匹配，试试「描述符」「GIL」「dataclass」</div>';
  res.classList.add('on');
}
input.addEventListener('input', run);
document.addEventListener('keydown', function (e) {
  if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) {
    e.preventDefault(); input.focus(); input.select();
  }
});
input.addEventListener('keydown', function (e) {
  if (e.key === 'Enter') {
    var a = res.querySelector('a');
    if (a) location.href = a.getAttribute('href');
  }
  if (e.key === 'Escape') { res.classList.remove('on'); input.blur(); }
});
document.addEventListener('click', function (e) {
  if (!e.target.closest('.hsearch')) res.classList.remove('on');
});
"""

UDECK_JS = r"""
(function(){
  var cur=1, n=__N__, slides=[].slice.call(document.querySelectorAll('.slide'));
  var dp=document.getElementById('dp'), cnt=document.getElementById('cnt');
  function go(i){
    cur=Math.max(1,Math.min(n,i));
    slides.forEach(function(s){s.classList.toggle('on',+s.dataset.s===cur)});
    dp.style.width=(cur/n*100)+'%';
    cnt.textContent=cur+' / '+n;
    if(location.hash!=='#s'+cur){try{history.replaceState(null,'','#s'+cur)}catch(e){}}
  }
  document.getElementById('prev').onclick=function(){go(cur-1)};
  document.getElementById('next').onclick=function(){go(cur+1)};
  document.addEventListener('keydown',function(e){
    if(e.key==='ArrowRight'||e.key===' '||e.key==='PageDown'){e.preventDefault();go(cur+1)}
    if(e.key==='ArrowLeft'||e.key==='PageUp'){e.preventDefault();go(cur-1)}
  });
  var x0=null;
  document.addEventListener('touchstart',function(e){x0=e.touches[0].clientX},{passive:true});
  document.addEventListener('touchend',function(e){
    if(x0===null)return;
    var dx=e.changedTouches[0].clientX-x0;
    if(Math.abs(dx)>50) go(cur+(dx<0?1:-1));
    x0=null;
  },{passive:true});
  var m=(location.hash||'').match(/^#s(\d+)$/);
  go(m?+m[1]:1);
})();
"""

def _section(md, name):
    m = re.search(r"### %s\s*\n(.*?)(?=\n### |\Z)" % name, md, re.S)
    return m.group(1) if m else ""

def _plain(s):
    s = re.sub(r"`([^`]*)`", r"\1", s)       # 去掉行内代码的反引号
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)  # 去掉粗体标记
    return re.sub(r"\s+", " ", s).strip()

def _points(md):
    out = []
    for line in _section(md, "关键点").splitlines():
        m = re.match(r"-\s+\*\*(.+?)\*\*\s*[：:]\s*(.+)", line.strip())
        if m:
            out.append((_plain(m.group(1)), _plain(m.group(2))))
            continue
        if line.strip().startswith("- "):
            out.append(("", _plain(line.strip()[2:])))
    return out[:4]

def _task(md):
    for line in _section(md, "动手").splitlines():
        t = line.strip()
        m = re.match(r"^\d+\.\s+(.+)", t)
        if m:
            return _plain(m.group(1))
    return "把本节的代码重敲一遍，改两处再跑。"

def _code(md):
    m = re.search(r"```python\n(.*?)```", md, re.S)
    if not m:
        return ""
    lines = m.group(1).rstrip().splitlines()
    if len(lines) > 18:
        lines = lines[:18] + ["# ..."]
    return "\n".join(lines)

def _checklist(outro):
    out = []
    for line in outro.splitlines():
        t = line.strip()
        if t.startswith("- [ ]"):
            out.append(_plain(t[5:].strip()))
    return out[:8]

def _slide(i, on, kicker, title, body):
    return (f'<section class="slide{" on" if on else ""}" data-s="{i}">'
            f'<div class="sk">{kicker}</div><h2>{title}</h2>{body}</section>')

def build_unit_decks(units):
    out_dir = os.path.join(WEB, "ppt", "u")
    os.makedirs(out_dir, exist_ok=True)
    cards = []
    for u in units:
        no = u["no"]
        chap, wk, _kw = UNIT_META[no]
        slides = [ _slide(1, True, f"UNIT {no} · 逐节课件",
                          f"单元 {no} · {html.escape(u['title'])}",
                          f'<div class="sub">{chap} · 4 节课 · 建议 {wk}</div>') ]
        lesson_links = []
        for L in u["lessons"]:
            g = (no - 1) * LESSONS_PER_UNIT + L["local"]
            pts = _points(L["md"])
            ul = "".join(
                f'<li>{("<b>" + html.escape(h) + "</b>：") if h else ""}{html.escape(b)}</li>'
                for h, b in pts) or f"<li>{html.escape(_plain(L['goal']))}</li>"
            slides.append(_slide(len(slides) + 1, False, f"第 {g} 课 · 目标与要点",
                                 html.escape(L["title"]),
                                 f'<div class="sub">{html.escape(_plain(L["goal"]))}</div><ul>{ul}</ul>'))
            code = _code(L["md"])
            code_html = (f'<pre><code>{html.escape(code)}</code></pre>' if code
                         else '<div class="sub">本节以概念与动手为主，没有独立代码块。</div>')
            slides.append(_slide(len(slides) + 1, False, f"第 {g} 课 · 代码与实操",
                                 "看一段，改一段",
                                 code_html + f'<div class="sub">动手：{html.escape(_task(L["md"]))}</div>'))
            lesson_links.append((L["local"], len(slides) - 1))

        checks = _checklist(u["outro"])
        cl = "".join(f"<li>{html.escape(x)}</li>" for x in checks) or "<li>完成本单元四节课的验收清单</li>"
        slides.append(_slide(len(slides) + 1, False, "单元验收", "过关清单",
                             f"<ul>{cl}</ul>"))

        body = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>单元 {no} 课件 · {html.escape(u['title'])}</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%234c3a9e'/%3E%3Ctext x='16' y='22' font-size='13' font-family='monospace' fill='%23fff' text-anchor='middle'%3EFP%3C/text%3E%3C/svg%3E">
<link rel="stylesheet" href="../../css/site.css">
</head><body>
<div class="deck">{''.join(slides)}</div>
<div class="dprog" id="dp"></div>
<div class="dnav">
  <a href="../../{no:02d}.html">← 单元 {no}</a>
  <button id="prev">←</button><span id="cnt">1 / {len(slides)}</span><button id="next">→</button>
  <a href="../../../index.html">课程首页</a>
</div>
<script>{UDECK_JS.replace('__N__', str(len(slides)))}</script>
</body></html>"""
        open(os.path.join(out_dir, f"{no:02d}.html"), "w", encoding="utf-8").write(body)

        rows = "".join(
            f'<a href="{no:02d}.html#s{s}"><span class="ln">{g}</span>第 {g} 课 · {html.escape(u["lessons"][g - (no - 1) * LESSONS_PER_UNIT - 1]["title"])}</a>'
            for g, s in [( (no-1)*LESSONS_PER_UNIT + loc, slide ) for loc, slide in lesson_links])
        cards.append(f"""<div class="uc">
  <div class="uh"><div class="un">{no}</div><div class="ut">{html.escape(u['title'])}</div></div>
  <div class="um">{chap} · {len(slides)} 页 · 每节 2 页</div>
  <div class="ul">{rows}</div>
  <div class="uf"><a href="{no:02d}.html">打开课件 →</a></div>
</div>""")

    hub = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>逐节课件 · 12 套</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%234c3a9e'/%3E%3Ctext x='16' y='22' font-size='13' font-family='monospace' fill='%23fff' text-anchor='middle'%3EFP%3C/text%3E%3C/svg%3E">
<link rel="stylesheet" href="../../css/site.css">
</head><body>
<div class="wrap">
  <div class="hero" style="padding:38px 40px">
    <div class="bdg">SLIDES · BY UNIT</div>
    <h1>逐节课件 · 12 套</h1>
    <p>每个单元一套：封面 + 每节「目标与要点 / 代码与实操」两页 + 验收页。
    键盘 ← → 翻页，也支持手机左右滑动。</p>
  </div>
  <div class="grid">{''.join(cards)}</div>
  <p style="margin-top:24px;font-size:12.5px;color:var(--muted)">
    <a href="../index.html">← 大纲课件（18 页）</a> ·
    <a href="../../../index.html">课程首页</a></p>
</div>
</body></html>"""
    open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8").write(hub)

def build_home(units):
    bank = json.load(open(os.path.join(SRC, "bank.json"), encoding="utf-8"))
    cards, lesson_js, idx = [], [], []
    for u in units:
        rows = []
        for L in u["lessons"]:
            g = (u["no"] - 1) * LESSONS_PER_UNIT + L["local"]
            rows.append(f'<a href="web/lessons/l{g:02d}.html"><span class="ln">{g:02d}</span>'
                        f'{html.escape(L["title"])}</a>')
            lesson_js.append({"n": g, "t": L["title"], "u": u["no"]})
            words = set()
            src = L["md"] + " " + BOOK.get(str(g), {}).get("deep", "")
            for raw in re.findall(r"`([^`\n]{2,40})`", src):
                if " " in raw.strip():
                    continue
                if not re.fullmatch(r"[A-Za-z0-9_./、]+", raw.strip()):
                    continue
                for w in re.split(r"[/、\s]+", raw.strip()):
                    if (re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*", w)
                            and w not in ("True", "False", "None")):
                        words.add(w)
            kws = sorted(words)
            idx.append({"t": f"第 {g} 课 · {L['title']}",
                        "s": f"单元 {u['no']} · {u['title']}",
                        "u": f"web/lessons/l{g:02d}.html", "k": "课节",
                        "w": " ".join(kws[:40])})
        cards.append(f"""<div class="uc">
  <div class="uh"><div class="un">{u['no']}</div>
    <div class="ut">{html.escape(u['title'])}</div></div>
  <div class="um">{UNIT_META[u['no']][0]} ｜ 建议 {UNIT_META[u['no']][1]}</div>
  <div class="ul">{''.join(rows)}</div>
  <div class="uf"><span data-prog="u{u['no']}">已学 0 / 4</span>
    <a style="margin-left:auto" href="web/{u['no']:02d}.html">单元讲义 →</a></div>
</div>""")
        idx.append({"t": f"单元 {u['no']} · {u['title']}",
                    "s": f"{UNIT_META[u['no']][0]} · 建议 {UNIT_META[u['no']][1]} · 4 节课",
                    "u": f"web/{u['no']:02d}.html", "k": "单元"})
        idx.append({"t": f"单元 {u['no']} 课件 · {u['title']}",
                    "s": "逐节课件 · 10 页（每节 2 页）",
                    "u": f"web/ppt/u/{u['no']:02d}.html", "k": "课件"})
    for q in bank:
        full = re.sub(r"[`*#>\[\]]", "", re.sub(r"\s+", " ", q["q"])).strip()
        idx.append({"t": f"{q['id']} · {full[:38]}",
                    "s": f"题库 · 单元 {q['unit']} · {q['level']}",
                    "u": f"web/bank.html#{q['id']}", "k": "题目",
                    "w": full[:400]})
    idx += [
        {"t": "课程目录 · 48 节课", "s": "按单元排列的课节索引",
         "u": "web/lessons/index.html", "k": "页面"},
        {"t": f"题库 · {BANK_N} 题", "s": "答案折叠、按单元筛选",
         "u": "web/bank.html", "k": "页面"},
        {"t": "关卡验收", "s": "两个阶段共 24 条",
         "u": "web/gates.html", "k": "页面"},
        {"t": "大纲课件", "s": "18 页，键盘翻页",
         "u": "web/ppt/index.html", "k": "页面"},
        {"t": "逐节课件 · 12 套", "s": "每单元一套，每节 2 页",
         "u": "web/ppt/u/index.html", "k": "页面"},
        {"t": "复习计划", "s": "艾宾浩斯遗忘曲线 · 6 轮间隔重复",
         "u": "web/review.html", "k": "页面"},
        {"t": f"总课表 · {SYL_TXT}", "s": "两种配速、三个阶段、关卡位置、每周节奏",
         "u": "web/syllabus.html", "k": "页面"},
        {"t": "实测数据", "s": "16 个写法快慢对比 · 本机 timeit 实跑",
         "u": "web/bench.html", "k": "页面"},
        {"t": "设计取舍 · 24 章", "s": "每个特性为什么这样设计、代价是什么",
         "u": "web/ch/index.html", "k": "页面"},
        {"t": "源码走读 · 12 篇", "s": "每单元一个完整程序 + 逐段讲解 + 真实输出",
         "u": "web/walk/index.html", "k": "页面"},
        {"t": "覆盖与自足性", "s": "24 章逐章对照、差异清单、怎么用这套课",
         "u": "web/coverage.html", "k": "页面"},
        {"t": "术语索引", "s": "标识符 → 课号，替代原书索引",
         "u": "web/terms.html", "k": "页面"},
    ]
    # 12 篇走读各一条：搜「描述符 走读」「asyncio 程序」能直达
    for p in load_walk():
        idx.append({"t": f"走读 {p['no']:02d} · {p['title']}",
                    "s": f"单元 {p['no']} · 完整程序 + 逐段讲解",
                    "u": f"web/walk/u{p['no']:02d}.html", "k": "走读"})
    # 24 篇设计长文各一条，方便搜「GIL 为什么这样设计」直达
    for c in load_design():
        idx.append({"t": f"第 {c['no']} 章 · {c['title']} · 设计取舍",
                    "s": f"单元 {c['unit']} · {UNIT_META[c['unit']][0]}",
                    "u": f"web/ch/{c['no']:02d}.html", "k": "设计"})

    by_no = {u["no"]: c for u, c in zip(units, cards)}
    groups = ""
    for name, chap, nos in PARTS:
        groups += (f'<div class="part"><b>{name}</b><span>{chap}</span></div>'
                   f'<div class="grid">' + "".join(by_no[n] for n in nos) + '</div>')

    body = f"""<div class="wrap">
  <div class="hero">
    <div class="bdg">ADVANCED · 第二版</div>
    <h1>《流畅的 Python》精读课</h1>
    <p>24 章拆成 12 个单元、48 节 90 分钟课。不背语法，专攻「为什么这样设计」
    与「代码怎么写得像 Python」。先修：能独立写函数与类。</p>
    <div class="st">
      <div><b>12</b><span>单元</span></div>
      <div><b>48</b><span>节课</span></div>
      <div><b>36</b><span>道题</span></div>
      <div><b>2</b><span>个关卡</span></div>
      <div><b>12</b><span>教学案例</span></div>
      <div><b>{SYL_RANGE}</b><span>周</span></div>
    </div>
  </div>

  <div class="csw">
    <a href="../index.html"><span class="ic">PY</span>
      <span><span class="t">Python 入门课</span>
      <span class="s">22 单元 · 111 节 · 从零到独立做项目</span></span></a>
    <a class="on" href="index.html"><span class="ic">FP</span>
      <span><span class="t">流畅的 Python 精读课</span>
      <span class="s">12 单元 · 48 节 · 进阶与源码阅读</span></span>
      <span class="cur">当前</span></a>
  </div>

  <div class="hsearch">
    <input id="fs" type="search" autocomplete="off" spellcheck="false"
           placeholder="搜单元 / 课节 / 题目：描述符、GIL、dataclass、切片 …（Ctrl + K）"
           aria-label="站内搜索">
    <div class="hres" id="fsRes"></div>
  </div>

  <div class="dash">
    <div class="dhead"><b>我的进度</b><span>数据只存在本机浏览器</span></div>
    <div class="drow"><span class="dlab">课节</span><div class="dbar"><i id="pL"></i></div>
      <span class="dval" id="tL">0 / 48</span></div>
    <div class="drow"><span class="dlab">单元</span><div class="dbar"><i id="pU"></i></div>
      <span class="dval" id="tU">0 / 12</span></div>
    <div class="drow"><span class="dlab">题库</span><div class="dbar"><i id="pB"></i></div>
      <span class="dval" id="tB">0 / {BANK_N}</span></div>
    <div class="dfoot"><a class="rbtn" id="rlink" href="web/lessons/l01.html">开始第 1 课</a>
      <span id="rtxt">按顺序学，每节 90 分钟</span>
      <span class="spacer"></span>
      <button class="mini-btn" id="expBtn" type="button" title="导出为 JSON，换电脑后导入">导出进度</button>
      <button class="mini-btn" id="impBtn" type="button" title="选择之前导出的 JSON">导入进度</button>
      <input id="impFile" type="file" accept=".json,application/json" hidden></div>
  </div>

  <div class="dash">
    <div class="dhead"><b>今日复习</b><span id="rvHint">按艾宾浩斯曲线排的 6 轮复习</span></div>
    <div class="drow"><span class="dlab">待复习</span><div class="dbar"><i id="rvP"></i></div>
      <span class="dval" id="rvT">0 项</span></div>
    <div class="dfoot"><a class="rbtn" id="rvLink" href="web/review.html">打开复习计划</a>
      <span id="rvTxt">学完一节课，当天就会自动排第一轮</span></div>
  </div>

  <div class="q">
    <a href="web/lessons/index.html"><b>课程目录</b><span>48 节课，按单元排列</span></a>
    <a href="web/syllabus.html"><b>总课表</b><span>{SYL_TXT} · 关卡在第几周</span></a>
    <a href="web/bank.html"><b>题库</b><span>{BANK_N} 题，答案折叠</span></a>
    <a href="web/gates.html"><b>关卡验收</b><span>两个阶段，逐条勾选</span></a>
    <a href="web/ppt/index.html"><b>大纲课件</b><span>18 页，键盘翻页</span></a>
    <a href="web/ppt/u/index.html"><b>逐节课件</b><span>12 套 · 每套 10 页</span></a>
    <a href="web/review.html"><b>复习计划</b><span>艾宾浩斯曲线 · 6 轮间隔重复</span></a>
    <a href="web/bench.html"><b>实测数据</b><span>16 个写法快慢对比 · 本机实跑</span></a>
    <a href="web/ch/index.html"><b>设计取舍</b><span>24 章 · 每个特性为什么这样设计</span></a>
    <a href="web/walk/index.html"><b>源码走读</b><span>12 个完整程序 · 逐段讲透</span></a>
    <a href="web/coverage.html"><b>覆盖与自足性</b><span>24 章逐章对照 + 差异清单</span></a>
    <a href="web/terms.html"><b>术语索引</b><span>标识符 → 课号，替代原书索引</span></a>
  </div>

  <div class="sec-h" id="units"><h2>12 个单元</h2><span>按教材五部分分组，点课节直接进</span></div>
  {groups}

  <p style="margin-top:30px;font-size:12px;color:var(--muted);line-height:1.8">
    教材：Fluent Python, 2nd Edition（Luciano Ramalho）｜ 课程化重写，
    示例按 Python 3.10+ 语法编写，3.11+ 特性在正文单独标注。<br>
    本站为纯静态页面，可离线打开；进度写入 localStorage，键前缀 <code>fl-</code>，与入门课互不干扰。</p>
</div>"""
    js = ("<script>\n(function(){\n" + HOME_JS
          .replace("__IDX__", json.dumps(idx, ensure_ascii=False))
          .replace("__LESSONS__", json.dumps(lesson_js, ensure_ascii=False)).replace("__BANKN__", str(BANK_N))
          + "\n})();\n</script>")
    out = page("《流畅的 Python》精读课", body, where="home", extra_body=js)
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(out)

CHAPTER_NAMES = {
    1: "数据模型", 2: "序列构成的数组", 3: "字典与集合", 4: "文本与字节序列",
    5: "数据类构建器", 6: "对象引用、可变性与垃圾回收", 7: "函数是一等对象",
    8: "类型提示", 9: "装饰器与闭包", 10: "设计模式", 11: "符合 Python 风格的对象",
    12: "序列的特殊方法", 13: "接口、协议与抽象基类", 14: "继承：优劣与替代",
    15: "类型提示进阶", 16: "运算符重载", 17: "迭代器、生成器与经典协程",
    18: "with、match 与其他语法糖", 19: "并发模型", 20: "并发执行器",
    21: "异步编程", 22: "动态属性与特性", 23: "描述符", 24: "类元编程",
}

def _chapters(book):
    m = re.search(r"第\s*([0-9]+(?:\s*[–\-,、]\s*[0-9]+)*)\s*章", book)
    if not m:
        return []
    out = []
    for part in re.split(r"[、,，]", m.group(1)):
        part = part.strip()
        if not part:
            continue
        if re.search(r"[–-]", part):
            a, b = re.split(r"[–-]", part)
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out

def build_coverage(units):
    """覆盖矩阵：24 章 × 课节，外加自足性说明。"""
    _wk = load_walk()
    walk_chars = sum(p["n_chars"] for p in _wk)
    walk_lines = sum(p["n_lines"] for p in _wk)
    total_chars = sum(len(u["intro"]) + len(u["outro"]) +
                      sum(len(L["md"]) for L in u["lessons"]) for u in units)
    total_blocks = sum(len(re.findall(r"```python", L["md"]))
                       for u in units for L in u["lessons"])
    ch_lessons = {}
    ch_spec = {}
    for u in units:
        for L in u["lessons"]:
            g = (u["no"] - 1) * LESSONS_PER_UNIT + L["local"]
            b = BOOK[str(g)]
            sec = re.sub(r"^第\s*[0-9–\-,、]+\s*章\s*", "", b["book"]).strip()
            for c in _chapters(b["book"]):
                ch_lessons.setdefault(c, []).append(g)
                if sec:
                    ch_spec.setdefault(c, []).append(sec)

    rows = []
    for c in sorted(range(1, 25)):
        gs = sorted(set(ch_lessons.get(c, [])))
        links = "".join(f'<a href="lessons/l{g:02d}.html">第 {g} 课</a>' for g in gs)
        tokens = []
        for sec in ch_spec.get(c, []):
            for tk in re.split(r"[、,，]", sec):
                tk = tk.strip()
                if tk == "综合":
                    tk = "综合运用"
                if tk and tk not in tokens:
                    tokens.append(tk)
        spec = "、".join(tokens) or "综合运用"
        u_no = (gs[0] - 1) // LESSONS_PER_UNIT + 1 if gs else 0
        rows.append(f'<tr><td class="cn">{c}</td><td>{CHAPTER_NAMES[c]}</td>'
                    f'<td class="u"><a href="{u_no:02d}.html">单元 {u_no}</a></td>'
                    f'<td class="sp">{html.escape(spec)}</td><td class="ls">{links}</td></tr>')

    urows = []
    for u in units:
        n = len(u["lessons"])
        chars = len(u["intro"]) + len(u["outro"]) + sum(len(L["md"]) for L in u["lessons"])
        case = re.search(r"## 综合案例：(.+?)\s*(?:\{:|$)", u["outro"])
        urows.append(f'<tr><td class="cn">{u["no"]}</td>'
                     f'<td><a href="{u["no"]:02d}.html">{html.escape(u["title"])}</a></td>'
                     f'<td>{n}</td><td>{chars:,}</td>'
                     f'<td>' + (f'<a href="{u["no"]:02d}.html#case-u{u["no"]:02d}">'
                            f'{html.escape(case.group(1))}</a>' if case else "—")
                     + '</td></tr>')

    body = f"""<div class="wrap">
  <div class="hero" style="padding:38px 40px">
    <div class="bdg">COVERAGE · 覆盖与自足性</div>
    <h1>课程能替代教材到什么程度</h1>
    <p>这张表是自查，不是宣传：24 章逐章标出对应课节与覆盖的小节范围，
    再列出课程提供、而原书没有的东西，以及课程<strong>不复制</strong>的部分。</p>
    <div class="st">
      <div><b>24</b><span>章全覆盖</span></div>
      <div><b>48</b><span>节课</span></div>
      <div><b>12</b><span>综合案例</span></div>
      <div><b>12</b><span>源码走读</span></div>
      <div><b>24</b><span>设计长文</span></div>
      <div><b>{total_chars // 1000}k + {walk_chars // 1000}k</b><span>正文字数（讲义 + 走读）</span></div>
      <div><b>{total_blocks}</b><span>Python 代码块</span></div>
    </div>
  </div>

  <div class="sec-h"><h2>逐章覆盖</h2><span>点课节直接进，点单元看完整讲义</span></div>
  <div class="tbl"><table>
    <thead><tr><th>章</th><th>主题</th><th>单元</th><th>覆盖小节</th><th>对应课节</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table></div>

  <div class="sec-h"><h2>单元体量</h2><span>字数含讲解、延伸、案例与验收</span></div>
  <div class="tbl"><table>
    <thead><tr><th>单元</th><th>标题</th><th>节数</th><th>正文</th><th>综合案例</th></tr></thead>
    <tbody>{''.join(urows)}</tbody>
  </table></div>

  <div class="sec-h"><h2>课程比原书多出来的</h2><span>这些是读书得不到的</span></div>
  <div class="g2box">
    <div class="cb"><b>可执行 + 已实跑</b><p>{total_blocks} 个代码块全部通过
      <code>compile()</code> 语法检查，重点示例逐条实跑并核对输出，注释里的结果不是猜的。</p></div>
    <div class="cb"><b>每节一条「延伸」</b><p>48 节各自补了一个原书同节里一句话带过、但实际会踩的细节，
      例如 dict 扩容、<code>__missing__</code> 与 <code>get</code> 的关系、<code>islice</code> 提前关闭生成器。</p></div>
    <div class="cb"><b>12 个完整案例</b><p>每单元一个「重构前 → 重构后」双版本案例，含差异表（收益与代价）与「下一步」，
      对应原书靠长案例教设计的那部分。</p></div>
    <div class="cb"><b>可检索</b><p>全站搜索（Ctrl+K）+ 术语索引 + 本覆盖表。
      原书靠纸质索引，这里靠关键词与课号。</p></div>
    <div class="cb"><b>可验收</b><p>每节有可验证的动手项，每单元有勾选清单，两章一个关卡，
      题库 {BANK_N} 题带折叠答案。</p></div>
    <div class="cb"><b>复习排程</b><p>按艾宾浩斯遗忘曲线自动排 6 轮复习（学完当天 / 1 / 3 / 7 / 15 / 30 天），
      <a href="review.html">复习计划页</a>给出今日待复习、逾期清单与记忆保持率估算。</p></div>
    <div class="cb"><b>实跑基准</b><p>35 种写法用 <code>timeit</code> best-of-N 与 <code>tracemalloc</code> 在同一台机器上对比，
      <a href="bench.html">实测数据页</a>顺手破除几个流传很广的「优化」迷信。</p></div>
    <div class="cb"><b>源码走读 12 篇</b><p><a href="walk/index.html">每个单元一个完整程序</a>
      （{walk_lines} 行代码，可直接跑），配 {walk_chars // 10000}.{(walk_chars % 10000) // 1000} 万字逐段讲解与
      <strong>实跑写回的真实输出</strong>，文末还有三处改动练习——
      这是最接近原书「长例子逐行讲」的部分。</p></div>
    <div class="cb"><b>设计取舍 24 章</b><p><a href="ch/index.html">24 篇长文</a>逐章讲「同一个问题，Python 给出了哪几种答案、各自付出什么代价」，
      这是读书时最容易跳过、写代码时最常用的部分。</p></div>
    <div class="cb"><b>三种载体</b><p>网页、离线便携包、安卓 App；课件 18 页总览 + 12 套逐节，
      支持键盘与触摸翻页。</p></div>
  </div>

  <div class="sec-h"><h2>课程不替代的部分</h2><span>诚实清单</span></div>
  <div class="cx">
    <p><b>1. 原书那种 100–300 行的「巨型案例」。</b>原书有些章节会完整打印上百行代码并逐段讲（Vector 的完整演化、
    拍卖程序、Lisp 解释器）。课程的替代方案是<a href="walk/index.html">源码走读 12 篇</a>：
    每单元一个 60–90 行的完整程序 + 逐段讲解 + 真实输出，覆盖同样的机制但不逐字复制原书代码——
    版权之外，缩短版的阅读节奏也更适合一次 90 分钟。想读那三个巨型案例的完整版，仍需原书。</p>
    <p><b>2. 更细的历史轶事与作者的个人品味。</b>「为什么 Python 社区最后选了这种设计」已由
    <a href="ch/index.html">设计取舍 24 章</a>逐篇论证（选择、候选方案、代价、如果重来）；
    原书里更细的开发轶事、邮件列表里的争论与作者的主观偏好，仍要回原书。</p>
    <p><b>3. 图表与排版。</b>原书的示意图、性能对比图没有复刻；课程用表格与实跑数字替代。</p>
    <p><b>4. 译名差异。</b>课程用「特殊方法 / 描述符 / 特性」等通用译法，与原书个别译名可能不同，看到同义词请按英文原名对齐。</p>
    <p><b>5. 版本时效。</b>课程以 Python 3.10+ 为准，3.11/3.12/3.13 的新特性单独标注；
    原书第 2 版成书于 3.10 时代，更新的内容以课程为准。</p>
  </div>

  <div class="sec-h"><h2>怎么用这套课</h2><span>给两种读者</span></div>
  <div class="g2box">
    <div class="cb"><b>没有原书</b><p>按单元顺序走：讲义 → <a href="walk/index.html">源码走读（跑一遍）</a>
    → 综合案例 → 题库 3 题 → 关卡勾选。
    每节末尾的「延伸」不要跳，那是原书一句话带过、实战最容易踩的地方。</p></div>
    <div class="cb"><b>有原书</b><p>把本表当索引：先看课节，再回原书对应小节读长论证。
    设计类问题（「为什么不那样写」）先查<a href="ch/index.html">设计取舍 24 章</a>，
    长例子先跑<a href="walk/index.html">源码走读</a>再看原书完整版——通常比直接啃原文快得多。</p></div>
  </div>

  <p style="margin-top:26px;font-size:12.5px;color:var(--muted)">
    <a href="../index.html">课程首页</a> ·
    <a href="terms.html">术语索引</a> ·
    <a href="lessons/index.html">课程目录</a></p>
</div>"""
    out = page("覆盖与自足性 · 24 章", body, where="web")
    open(os.path.join(WEB, "coverage.html"), "w", encoding="utf-8").write(out)
    return total_chars

def build_terms(units):
    """术语索引：从讲义行内代码里抽标识符，按首字符分组，替代原书索引。"""
    STOP = {"python", "Python", "True", "False", "None", "self", "cls", "print",
            "str", "int", "float", "list", "dict", "set", "tuple", "len", "os", "sys"}
    index = {}
    for u in units:
        for L in u["lessons"]:
            g = (u["no"] - 1) * LESSONS_PER_UNIT + L["local"]
            for raw in re.findall(r"`([^`\n]{2,48})`", L["md"]):
                t = raw.strip()
                if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", t):
                    continue
                if len(t) < 3 or t in STOP or t.endswith("."):
                    continue
                if re.match(r"^[a-z]\.[A-Za-z_]", t):      # a.__add__ / c.maps 这类用法
                    continue
                if "__" in t and not t.startswith("__"):    # Bag.__iadd__ 只保留 __iadd__
                    continue
                index.setdefault(t, []).append(g)

    groups = {}
    for t, gs in index.items():
        key = t[0].upper() if t[0].isalpha() else "_"
        groups.setdefault(key, []).append((t, sorted(set(gs))))

    order = sorted(k for k in groups if k != "_") + (["_"] if "_" in groups else [])
    blocks = []
    for k in order:
        items = sorted(groups[k], key=lambda x: x[0].lower())
        lis = "".join(
            f'<li data-t="{html.escape(t.lower())}"><code>{html.escape(t)}</code>'
            + "".join(f'<a href="lessons/l{g:02d}.html">{g}</a>' for g in gs[:4])
            + ("<span>+%d</span>" % (len(gs) - 4) if len(gs) > 4 else "")
            + "</li>" for t, gs in items)
        blocks.append(f'<div class="ig"><div class="ih">{k}</div><ul>{lis}</ul></div>')

    body = f"""<div class="wrap">
  <div class="hero" style="padding:36px 40px">
    <div class="bdg">INDEX · 术语索引</div>
    <h1>术语索引 · {len(index)} 条</h1>
    <p>从 48 节课的正文里自动抽出的标识符，右侧数字是课号，点进去就是讲解位置。
    相当于原书末尾的索引，但每条都指向可运行代码。</p>
  </div>
  <div class="hsearch"><input id="tq" type="search" autocomplete="off" spellcheck="false"
    placeholder="输入过滤：__slots__、islice、lru_cache …" aria-label="术语过滤">
    <div class="hres" id="tqRes"></div></div>
  <div class="idx" id="idx">{''.join(blocks)}</div>
  <p style="margin-top:24px;font-size:12.5px;color:var(--muted)">
    <a href="../index.html">课程首页</a> ·
    <a href="coverage.html">覆盖与自足性</a> ·
    <a href="lessons/index.html">课程目录</a></p>
</div>
<script>
(function(){{
  var q = document.getElementById('tq');
  var items = [].slice.call(document.querySelectorAll('#idx li'));
  var groupsEls = [].slice.call(document.querySelectorAll('#idx .ig'));
  function run(){{
    var v = q.value.trim().toLowerCase(), n = 0;
    items.forEach(function(li){{
      var hit = !v || li.dataset.t.indexOf(v) >= 0;
      li.style.display = hit ? '' : 'none';
      if (hit) n++;
    }});
    groupsEls.forEach(function(g){{
      var any = [].slice.call(g.querySelectorAll('li')).some(function(li){{ return li.style.display !== 'none'; }});
      g.style.display = any ? '' : 'none';
    }});
    var res = document.getElementById('tqRes');
    if (!v) {{ res.classList.remove('on'); res.textContent = ''; return; }}
    res.classList.add('on');
    res.textContent = n ? ('命中 ' + n + ' 条') : '没有匹配的术语';
  }}
  q.addEventListener('input', run);
  q.addEventListener('keydown', function(e){{ if (e.key === 'Escape') {{ q.value = ''; run(); q.blur(); }} }});
}})();
</script>"""
    out = page(f"术语索引 · {len(index)} 条", body, where="web")
    open(os.path.join(WEB, "terms.html"), "w", encoding="utf-8").write(out)
    return len(index)

# 艾宾浩斯复习间隔（学完后的天数）：当天 → 2 → 4 → 8 → 16 → 31 天
REVIEW_STAGES = [
    (0,  "当天复盘", "合上讲义，凭记忆写下本课 3 个关键点，再自答一遍验收清单"),
    (1,  "第 2 天",  "重读「关键点」小节，并做完题库里本单元对应的题目"),
    (3,  "第 4 天",  "重跑本课示例代码，改一个参数观察结果如何变化"),
    (7,  "第 8 天",  "重读单元讲义中本课的部分，把综合案例按自己的场景再改一版"),
    (15, "第 16 天", "合上资料讲一遍（费曼技巧），卡住的地方记下来回看对应段落"),
    (30, "第 31 天", "只看目录复述本课结构，并过一遍关卡里对应的验收条目"),
]

def build_syllabus(units):
    """总课表：标准 12 周 / 轻量 24 周两种配速。

    入门课一直有「总课表 + 阶段 + 关卡位置」，进阶课原来只有一个「建议 2 周」，
    学习者拿不到全局进度感，也不知道关卡卡在第几周。
    """
    import fluent_syllabus as fs
    body = fs.build_body(units, BOOK)
    a, b = fs.totals(units)
    out = page(f"总课表 · 标准 {a} 周 / 轻量 {b} 周", body, where="web")
    open(os.path.join(WEB, "syllabus.html"), "w", encoding="utf-8").write(out)
    return len(units)

def build_review(units):
    """复习计划页：按艾宾浩斯遗忘曲线排 6 轮复习，全部在本机 localStorage 完成。"""
    lessons = []
    for u in units:
        for L in u["lessons"]:
            g = (u["no"] - 1) * LESSONS_PER_UNIT + L["local"]
            lessons.append({"n": g, "t": L["title"], "u": u["no"]})
    n_lessons = len(lessons)
    n_rounds = n_lessons * len(REVIEW_STAGES)

    stage_rows = "".join(
        f"<tr><td>{i}</td><td>{html.escape(lab)}</td><td>学完第 {off} 天</td>"
        f"<td>{html.escape(task)}</td></tr>"
        for i, (off, lab, task) in enumerate(REVIEW_STAGES, 1))

    body = f"""<div class="wrap">
  <div class="hero" style="padding:38px 42px 34px">
    <div class="bdg">REVIEW · 艾宾浩斯遗忘曲线</div>
    <h1>复习计划</h1>
    <p>每学完一节课，自动排 6 轮复习：当天 → 第 2 天 → 第 4 天 → 第 8 天 → 第 16 天 → 第 31 天。
    每轮只花 5–15 分钟，做完点「标记完成」，后面的轮次自动接上。
    错过时间会标成逾期，越早补上越省力。进度只存本机浏览器。</p>
    <div class="st">
      <div><b>{len(REVIEW_STAGES)}</b><span>轮复习</span></div>
      <div><b>{n_lessons}</b><span>节课</span></div>
      <div><b>{n_rounds}</b><span>个复习点</span></div>
    </div>
  </div>

  <div class="dash">
    <div class="dhead"><b>复习看板</b><span id="rvSum">统计中…</span></div>
    <div class="drow"><span class="dlab">今日</span><div class="dbar"><i id="rvPT"></i></div>
      <span class="dval" id="rvTT">0 项</span></div>
    <div class="drow"><span class="dlab">逾期</span><div class="dbar"><i id="rvPO"></i></div>
      <span class="dval" id="rvTO">0 项</span></div>
    <div class="drow"><span class="dlab">轮次</span><div class="dbar"><i id="rvPR"></i></div>
      <span class="dval" id="rvTR">0 / {n_rounds}</span></div>
    <div class="drow"><span class="dlab">掌握</span><div class="dbar"><i id="rvPM"></i></div>
      <span class="dval" id="rvTM">0 / {n_lessons} 课</span></div>
  </div>

  <div class="rv-sec"><h2>今日待复习</h2><span id="nowSub">含逾期未补的</span></div>
  <div id="rvNow"></div>

  <div class="rv-sec"><h2>未来安排</h2><span>按到期日分组</span></div>
  <div id="rvPlan"></div>

  <div class="rv-sec"><h2>记忆保持率</h2><span>估算值，越靠前越该先复习</span></div>
  <div class="dash" style="padding:8px 18px"><div id="rvCurve"></div></div>

  <div class="rv-rule">
    <h3>为什么是这几个时间点</h3>
    <p>艾宾浩斯遗忘曲线描述的是「学完后记忆保持率随时间下降」的规律：记住的内容在
    最初几小时掉得最快，随后趋于平缓。在快要忘掉的时点做一次主动回忆，遗忘速度会明显变慢，
    这就是间隔重复（spaced repetition）。下表是本课程采用的时间点，来自曲线上
    「掉得快」与「快掉完」的两段密集区，兼顾每天只学一节课的节奏。</p>
    <table>
      <thead><tr><th>轮次</th><th>时点</th><th>距学完</th><th>做什么（5–15 分钟）</th></tr></thead>
      <tbody>{stage_rows}</tbody>
    </table>
    <p><b>记忆保持率怎么算：</b>用指数衰减 R = e<sup>-t/S</sup> 估算。基础稳定期 S = 2.5 天，
    每完成一轮复习 S ×2，所以复习得越及时，同一节课后面越难忘。这里的数字只是提醒工具，
    真正的标准是「合上资料能不能讲出来」。</p>
    <p><b>使用建议：</b>① 今天排的任务今天清，逾期超过 3 轮建议直接重学该课；
    ② 复习时先自己回忆再看资料，效果远好过重读；③ 与题库配合：标记「待复习」的题优先做。</p>
  </div>

  <div class="rv-foot">
    <a href="lessons/index.html">课程目录</a> ·
    <a href="bank.html">题库</a> ·
    <a href="gates.html">关卡验收</a> ·
    <a href="../index.html">课程首页</a>
    <span style="flex:1"></span>
    <button id="rvClear" type="button">清空复习记录</button>
  </div>
</div>"""

    js = """<script>
(function(){
  var LESSONS = __LESSONS__, STAGES = __STAGES__;
  var LKEY = 'fl-lesson-v1', RKEY = 'fl-review-v1';
  var DAY = 86400000, WEEK = ['日','一','二','三','四','五','六'];

  function read(k){ try{ var v = JSON.parse(localStorage.getItem(k)); return v == null ? {} : v }catch(e){ return {} } }
  function write(k, v){ try{ localStorage.setItem(k, JSON.stringify(v)) }catch(e){} }
  function mid(t){ var d = new Date(t); d.setHours(0,0,0,0); return d.getTime(); }
  function pad(n){ return (n < 10 ? '0' : '') + n; }
  function dlabel(t){ var d = new Date(t); return pad(d.getMonth()+1) + '-' + pad(d.getDate()) + ' 周' + WEEK[d.getDay()]; }
  function esc(s){ return String(s).replace(/[&<>"]/g, function(c){
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function lp(n){ return (n < 10 ? '0' : '') + n; }

  var TODAY = mid(Date.now());
  var L = read(LKEY), R = read(RKEY), moved = false, pruned = false;
  for (var k in L) if (L[k] === 1) { L[k] = Date.now(); moved = true; }
  if (moved) write(LKEY, L);
  for (var k2 in R) if (!L[k2]) { delete R[k2]; pruned = true; }
  if (pruned) write(RKEY, R);

  function collect(){
    var due = [], plan = [], rows = [], totalDone = 0, mastered = 0;
    LESSONS.forEach(function(x){
      var t = L[x.n];
      if (!t) return;
      var learned = mid(t), rs = R[x.n] || [], done = 0, last = t;
      STAGES.forEach(function(s, i){
        if (rs[i]) { done++; if (rs[i] > last) last = rs[i]; }
      });
      totalDone += done;
      if (done === STAGES.length) mastered++;
      var S = 2.5;
      for (var i = 0; i < done; i++) S *= 2;
      var ret = Math.exp(-((TODAY - mid(last)) / DAY) / S);
      rows.push({ x: x, done: done, ret: ret, last: last });
      STAGES.forEach(function(s, i){
        if (rs[i]) return;
        var d = learned + s[0] * DAY;
        var item = { x: x, i: i, lab: s[1], task: s[2], due: d,
                     od: Math.round((TODAY - d) / DAY) };
        if (d <= TODAY) due.push(item); else plan.push(item);
      });
    });
    due.sort(function(a, b){ return a.due - b.due; });
    plan.sort(function(a, b){ return a.due - b.due; });
    rows.sort(function(a, b){ return a.ret - b.ret; });
    return { due: due, plan: plan, rows: rows, totalDone: totalDone, mastered: mastered };
  }

  function itemHtml(it, overdue){
    var when;
    if (it.od > 0) when = '原定 ' + dlabel(it.due);
    else if (it.od === 0) when = '今天到期';
    else when = dlabel(it.due) + ' 到期';
    var meta = '单元 ' + it.x.u + ' · 第 ' + (it.i + 1) + ' / ' + STAGES.length + ' 轮 · ' + it.lab
      + ' · ' + when;
    return '<div class="rv-item' + (overdue ? ' over' : '') + '">'
      + '<div class="rv-no">' + lp(it.x.n) + '</div><div class="rv-bd">'
      + '<div class="rv-t">第 ' + it.x.n + ' 课 · ' + esc(it.x.t) + '</div>'
      + '<div class="rv-m">' + esc(meta)
      + (it.od > 0 ? ' · <span class="od">逾期 ' + it.od + ' 天</span>' : '') + '</div>'
      + '<div class="rv-task">任务：' + esc(it.task) + '</div>'
      + '<div class="rv-act">'
      + '<a href="lessons/l' + lp(it.x.n) + '.html">去复习</a>'
      + '<a href="ppt/u/' + lp(it.x.u) + '.html">看课件</a>'
      + '<a href="bank.html#u' + it.x.u + '">做本题</a>'
      + '<button type="button" data-g="' + it.x.n + '" data-i="' + it.i + '">标记完成</button>'
      + '</div></div></div>';
  }

  function render(){
    var d = collect();
    var todayN = 0, overN = 0;
    d.due.forEach(function(it){ if (it.od > 0) overN++; else todayN++; });

    document.getElementById('rvTT').textContent = todayN + ' 项';
    document.getElementById('rvTO').textContent = overN + ' 项';
    document.getElementById('rvTR').textContent = d.totalDone + ' / ' + (LESSONS.length * STAGES.length);
    document.getElementById('rvTM').textContent = d.mastered + ' / ' + LESSONS.length + ' 课';
    document.getElementById('rvPT').style.width = (todayN / Math.max(1, LESSONS.length) * 100) + '%';
    document.getElementById('rvPO').style.width = (overN / Math.max(1, LESSONS.length) * 100) + '%';
    document.getElementById('rvPR').style.width = (d.totalDone / (LESSONS.length * STAGES.length) * 100) + '%';
    document.getElementById('rvPM').style.width = (d.mastered / LESSONS.length * 100) + '%';
    document.getElementById('rvSum').textContent = d.rows.length
      ? ('已学 ' + d.rows.length + ' 课 · 待复习 ' + (d.due.length + d.plan.length) + ' 项')
      : '还没有已学完的课节';

    var now = document.getElementById('rvNow');
    if (!d.rows.length) {
      now.innerHTML = '<div class="rv-empty">还没有已学完的课节。去完成'
        + ' <a href="lessons/l01.html">第 1 课</a>，当天就会生成第一轮复习任务。</div>';
    } else if (!d.due.length) {
      now.innerHTML = '<div class="rv-empty">今天没有待复习的课，保持住 👍<br>'
        + '下一批安排见下方「未来安排」。</div>';
    } else {
      now.innerHTML = d.due.map(function(it){ return itemHtml(it, it.od > 0); }).join('');
    }

    var pl = document.getElementById('rvPlan');
    if (!d.plan.length) {
      pl.innerHTML = '<div class="rv-empty">未来两周没有新的复习点——要么都复习完了，要么还没开始学。</div>';
    } else {
      var html = '', cur = '', shown = 0;
      d.plan.forEach(function(it){
        if (shown >= 40) return;
        var lab = dlabel(it.due);
        if (lab !== cur) {
          cur = lab;
          html += '<div class="rv-day"><b>' + lab + '</b></div>';
        }
        html += itemHtml(it, false);
        shown++;
      });
      if (d.plan.length > shown) {
        html += '<div class="rv-empty">其余 ' + (d.plan.length - shown) + ' 项在更远的日期，学完后面的课再来看。</div>';
      }
      pl.innerHTML = html;
    }

    var cv = document.getElementById('rvCurve');
    if (!d.rows.length) {
      cv.innerHTML = '<div class="rv-empty" style="border:none">学完第一节课后，这里会显示每节课的记忆保持率。</div>';
    } else {
      cv.innerHTML = d.rows.map(function(r){
        var pct = Math.round(r.ret * 100);
        var cls = pct >= 80 ? '' : (pct >= 50 ? ' mid' : ' low');
        var days = Math.round((TODAY - mid(r.last)) / DAY);
        return '<div class="rv-c"><div class="rv-cn">' + lp(r.x.n) + '</div>'
          + '<div class="rv-cb"><i class="' + cls + '" style="width:' + Math.max(3, pct) + '%"></i></div>'
          + '<div class="rv-cv">' + pct + '%</div>'
          + '<div class="rv-ct">第 ' + r.x.n + ' 课 · ' + esc(r.x.t)
          + ' · 已复习 ' + r.done + ' 轮 · 距上次 ' + days + ' 天</div></div>';
      }).join('');
    }
  }

  document.addEventListener('click', function(e){
    var b = e.target.closest('button[data-g]');
    if (!b) return;
    var g = +b.dataset.g, i = +b.dataset.i;
    var r = read(RKEY), a = r[g] || (r[g] = []);
    a[i] = Date.now();
    write(RKEY, r);
    R = r;
    render();
  });
  document.getElementById('rvClear').addEventListener('click', function(){
    if (!confirm('清空全部复习记录？课节进度不受影响，复习轮次会重新排。')) return;
    write(RKEY, {});
    R = {};
    render();
  });
  window.addEventListener('focus', render);
  document.addEventListener('visibilitychange', function(){
    if (!document.hidden) render();
  });
  render();
})();
</script>""".replace("__LESSONS__", json.dumps(lessons, ensure_ascii=False)) \
       .replace("__STAGES__", json.dumps([[o, l, t] for o, l, t in REVIEW_STAGES],
                                         ensure_ascii=False))

    out = page("复习计划 · 艾宾浩斯遗忘曲线", body, where="web", extra_body=js)
    open(os.path.join(WEB, "review.html"), "w", encoding="utf-8").write(out)
    return len(lessons)

BENCH_JSON = os.path.join(ROOT, "bench", "results.json")

def _fmt_sec(s):
    if s >= 1:
        return f"{s:.2f} s"
    if s >= 0.001:
        return f"{s * 1000:.2f} ms"
    return f"{s * 1e6:.1f} µs"

def build_bench(units):
    """实测数据页：读 bench/results.json（由 tools/bench_fluent.py 生成）。"""
    unit_title = {u["no"]: u["title"] for u in units}
    if not os.path.exists(BENCH_JSON):
        body = """<div class="wrap">
  <div class="hero" style="padding:38px 42px 34px">
    <div class="bdg">BENCH · 实测数据</div>
    <h1>实测数据</h1>
    <p>本页由 <code>tools/bench_fluent.py</code> 实跑生成，现在还没有结果文件。</p>
  </div>
  <div class="rv-empty">在项目根目录执行
    <code>python tools/bench_fluent.py</code>，会生成 <code>bench/results.json</code>，
    再重建站点即可看到数据。</div>
</div>"""
        out = page("实测数据 · 尚未生成", body, where="web")
        open(os.path.join(WEB, "bench.html"), "w", encoding="utf-8").write(out)
        return 0

    data = json.load(open(BENCH_JSON, encoding="utf-8"))
    env, cases = data["env"], data["cases"]
    cards = []
    for c in sorted(cases, key=lambda x: (x["unit"], x["id"])):
        rows = []
        best = min(v["per"] for v in c["variants"])
        for v in c["variants"]:
            ratio = v["per"] / best if best else 1
            tag = ('<b class="fast">最快</b>' if ratio <= 1.001
                   else (f'{ratio:.0f}×' if ratio >= 10 else f'{ratio:.1f}×'))
            mem = (f'<td class="num">{v["mem"] / 1048576:.2f} MB</td>'
                   if v.get("mem") is not None else
                   ('<td class="num">—</td>' if c["mem"] else ""))
            rows.append(
                f'<tr><td>{html.escape(v["name"])}</td>'
                f'<td class="num">{_fmt_sec(v["per"])}</td>'
                f'<td class="num">{tag}</td>{mem}</tr>')
        mem_head = '<th>峰值内存</th>' if c["mem"] else ""
        cards.append(f"""<div class="bnch">
  <div class="bh"><span class="bu">单元 {c['unit']} · {html.escape(unit_title.get(c['unit'], ''))}</span>
    <b>{html.escape(c['q'])}</b></div>
  <div class="btw"><table>
    <thead><tr><th>写法</th><th>单次耗时</th><th>相对最快</th>{mem_head}</tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table></div>
  <p class="bn">{html.escape(c['note'])}</p>
</div>""")

    body = f"""<div class="wrap">
  <div class="hero" style="padding:38px 42px 34px">
    <div class="bdg">BENCH · 实测数据</div>
    <h1>实测数据 · {len(cases)} 个取舍</h1>
    <p>课程里每一次「该用哪个写法」的判断，都在本机实跑过。数字本身会随机器和
    Python 版本变化，<b>倍数关系才是能带走的结论</b>；每个案例下面都写了适用边界。</p>
    <div class="st">
      <div><b>{len(cases)}</b><span>个案例</span></div>
      <div><b>{sum(len(c['variants']) for c in cases)}</b><span>种写法</span></div>
      <div><b>{sum(1 for c in cases if c['mem'])}</b><span>个含内存测量</span></div>
    </div>
  </div>

  <div class="benv">
    <b>运行环境</b>
    <span>Python {html.escape(env['python'])}（{html.escape(env['impl'])}）</span>
    <span>{html.escape(env['system'])} · {html.escape(env['machine'])}</span>
    <span>{html.escape(env['date'])}</span>
    <p>计时：<code>timeit</code>，每个写法重复 {data['method']['repeat']} 轮取最快一轮；
    内存：<code>tracemalloc</code> 峰值，跑 {data['method']['mem'].split('，')[-1]}。
    换机器请重新运行 <code>tools/bench_fluent.py</code> 生成本页。</p>
  </div>

  {''.join(cards)}

  <p style="margin-top:26px;font-size:12.5px;color:var(--muted);line-height:1.9">
    <b>怎么读这些数字：</b>① 先看倍数，1.0× 是同一案例里最快的写法；
    ② 小于 1.5× 的差距基本是噪声，按可读性选；③ 内存列只在标注了的案例里出现，
    用 tracemalloc 量的是 Python 层分配的峰值，不含解释器本身；
    ④ 所有案例的代码都在 <code>course-fluent/bench.json</code> 里，可以自己改参数重跑。</p>
</div>"""
    out = page(f"实测数据 · {len(cases)} 个取舍", body, where="web")
    open(os.path.join(WEB, "bench.html"), "w", encoding="utf-8").write(out)
    return len(cases)

def load_design():
    """读 chapters.json + design/chNN.md，校验 24 章齐全、标题与 CHAPTER_NAMES 一致。"""
    meta = json.load(open(os.path.join(DESIGN, "chapters.json"), encoding="utf-8"))
    rows = meta["chapters"]
    if [r["ch"] for r in rows] != list(range(1, 25)):
        raise SystemExit("chapters.json 必须覆盖第 1–24 章")
    out = []
    for r in rows:
        no = r["ch"]
        fn = os.path.join(DESIGN, f"ch{no:02d}.md")
        if not os.path.exists(fn):
            raise SystemExit(f"缺少设计长文：{fn}")
        md = open(fn, encoding="utf-8").read()
        m = re.match(r"@@ch(\d+)\|(.+)", md)
        if not m or int(m.group(1)) != no:
            raise SystemExit(f"{fn} 首行应为「@@ch{no:02d}|标题」")
        title = m.group(2).strip()
        if title != CHAPTER_NAMES[no]:
            raise SystemExit(f"第 {no} 章标题不一致：文件「{title}」"
                             f"vs 教材「{CHAPTER_NAMES[no]}」")
        body = md[m.end():].strip()
        out.append({"no": no, "title": title, "unit": r["unit"],
                    "md": body, "file": f"ch{no:02d}.md"})
    return out

def build_design(units):
    """设计取舍长文：24 章各一页 + 总览页。"""
    chapters = load_design()
    unit_title = {u["no"]: u["title"] for u in units}
    by_unit = {}
    for c in chapters:
        by_unit.setdefault(c["unit"], []).append(c)

    # 每章一页
    for c in chapters:
        body_html = dedupe_ids(md2html(c["md"]))
        lo, hi = c["no"] - 1, c["no"] + 1
        prev = (f'<a href="{lo:02d}.html"><small>← 上一章</small>'
                f'<b>第 {lo} 章 · {html.escape(chapters[lo - 1]["title"])}</b></a>'
                if lo >= 1 else "")
        nxt = (f'<a class="nx" href="{hi:02d}.html"><small>下一章 →</small>'
               f'<b>第 {hi} 章 · {html.escape(chapters[hi - 1]["title"])}</b></a>'
               if hi <= len(chapters) else "")
        u = c["unit"]
        body = f"""<div class="layout">
  <main class="main">
    <div class="head">
      <div class="kicker"><span class="kno">第 {c['no']} 章</span>
        <span class="kwk">单元 {u} · {html.escape(unit_title[u])}</span>
        <span class="ku">设计取舍</span></div>
      <h1>{html.escape(c['title'])}</h1>
      <p class="goal">原书这一章的写法，Python 为什么这样选、换别的要付什么代价。</p>
    </div>
    {body_html}
    <div class="pn">{prev or '<span></span>'}{nxt or '<span></span>'}</div>
    <p style="font-size:12.5px;color:var(--muted);margin-top:14px">
      <a href="index.html">设计取舍总览</a> ·
      <a href="../{u:02d}.html">单元 {u} 讲义</a> ·
      <a href="../../index.html">课程首页</a></p>
  </main>
</div>"""
        out = page(f"第 {c['no']} 章 · {c['title']} · 设计取舍", body, where="lesson")
        open(os.path.join(WEB, "ch", f"{c['no']:02d}.html"), "w",
             encoding="utf-8").write(out)

    # 总览页：按单元分组
    groups = []
    for u in sorted(by_unit):
        rows = "".join(
            f'<a href="{c["no"]:02d}.html"><span class="no">{c["no"]:02d}</span>'
            f'<span class="tx">{html.escape(c["title"])}</span></a>'
            for c in by_unit[u])
        groups.append(f"""<div class="uc">
  <div class="uh"><div class="un">{u}</div>
    <div class="ut">{html.escape(unit_title[u])}</div></div>
  <div class="um">单元 {u} · {UNIT_META[u][0]}</div>
  <div class="nlist">{rows}</div>
  <div class="uf"><a href="../{u:02d}.html">单元讲义 →</a></div>
</div>""")
    body = f"""<div class="wrap">
  <div class="hero" style="padding:38px 42px 34px">
    <div class="bdg">DESIGN · 设计取舍</div>
    <h1>设计取舍 · 24 章</h1>
    <p>原书每一章都在回答同一个问题：这个特性为什么长成这样，换一种写法要付出什么。
    这里把 24 章各浓缩成一页——选择、落选的替代、当时的约束、代价与反例、如果重来。
    读代码之前先读它，能少走很多「早知道就好了」的弯路。</p>
    <div class="st">
      <div><b>24</b><span>章</span></div>
      <div><b>12</b><span>个单元</span></div>
    </div>
  </div>
  <div class="grid">{''.join(groups)}</div>
  <p style="margin-top:26px;font-size:12.5px;color:var(--muted);line-height:1.9">
    每章对应原书一章的写作动机；具体语法与代码在 <a href="../01.html">单元讲义</a>，
    逐字对照见 <a href="../coverage.html">覆盖与自足性</a>。</p>
</div>"""
    out = page("设计取舍 · 24 章", body, where="lesson")
    open(os.path.join(WEB, "ch", "index.html"), "w", encoding="utf-8").write(out)
    return len(chapters)

def load_walk():
    """读 walk/uNN.md：校验 12 篇齐全、首行是「@@uNN|标题」。"""
    out = []
    for no in range(1, 13):
        fn = os.path.join(WALK, f"u{no:02d}.md")
        if not os.path.exists(fn):
            raise SystemExit(f"缺少源码走读：{fn}")
        md = open(fn, encoding="utf-8").read()
        m = re.match(r"@@u(\d\d)\|(.+)", md)
        if not m or int(m.group(1)) != no:
            raise SystemExit(f"{fn} 首行应为「@@u{no:02d}|标题」")
        body = md[m.end():].strip()
        lead = ""
        for line in body.splitlines():
            if line.startswith("> "):
                lead = line[2:].strip()
                break
        # 统计：去掉代码块后的正文字数 + 代码行数（覆盖页要用）
        plain = re.sub(r"```[a-z]*\n.*?```", "", body, flags=re.S)
        n_chars = len(re.sub(r"\s+", "", plain))
        n_lines = sum(len(b.splitlines())
                      for b in re.findall(r"```python\n(.*?)```", body, re.S))
        # 运行输出块单独渲染成 <pre>，不用 pygments（它不是 Python 源码）
        body = re.sub(r"```text\n(.*?)```",
                      lambda x: '<pre class="out"><code>'
                                + html.escape(x.group(1).rstrip("\n")) + "</code></pre>",
                      body, flags=re.S)
        out.append({"no": no, "title": m.group(2).strip(), "lead": lead, "md": body,
                    "n_chars": n_chars, "n_lines": n_lines})
    return out

def build_walk(units):
    """源码走读：12 篇各一页 + 总览页。"""
    posts = load_walk()
    unit_title = {u["no"]: u["title"] for u in units}
    by_no = {p["no"]: p for p in posts}

    for p in posts:
        no = p["no"]
        body_html = dedupe_ids(md2html(p["md"]))
        prev = (f'<a href="u{no-1:02d}.html"><small>← 上一篇</small>'
                f'<b>单元 {no-1} · {html.escape(by_no[no-1]["title"])}</b></a>'
                if no > 1 else "<span></span>")
        nxt = (f'<a class="nx" href="u{no+1:02d}.html"><small>下一篇 →</small>'
               f'<b>单元 {no+1} · {html.escape(by_no[no+1]["title"])}</b></a>'
               if no < 12 else "<span></span>")
        body = f"""<div class="layout">
  <main class="main">
    <div class="head">
      <div class="kicker"><span class="kno">走读 {no:02d}</span>
        <span class="kwk">单元 {no} · {html.escape(unit_title[no])}</span>
        <span class="ku">{UNIT_META[no][0]}</span></div>
      <h1>{html.escape(p['title'])}</h1>
      <p class="goal">一个可以整段复制运行的完整程序 + 逐段讲解 + 真实输出。
        先跑一遍，再对着输出读讲解，最后做文末的三处改动。</p>
    </div>
    {body_html}
    <div class="pn">{prev}{nxt}</div>
    <p style="font-size:12.5px;color:var(--muted);margin-top:14px">
      <a href="index.html">走读总览</a> ·
      <a href="../{no:02d}.html">单元 {no} 讲义</a> ·
      <a href="../../index.html">课程首页</a></p>
  </main>
</div>"""
        out = page(f"走读 {no:02d} · {p['title']}", body, where="lesson")
        open(os.path.join(WEB, "walk", f"u{no:02d}.html"), "w",
             encoding="utf-8").write(out)

    cards = "".join(f"""<div class="uc">
  <div class="uh"><div class="un">{p['no']}</div>
    <div class="ut">{html.escape(p['title'])}</div></div>
  <div class="um">单元 {p['no']} · {html.escape(unit_title[p['no']])}</div>
  <div class="wl">{html.escape(_plain(p['lead']))}</div>
  <div class="uf"><a href="u{p['no']:02d}.html">打开走读 →</a></div>
</div>""" for p in posts)
    body = f"""<div class="wrap">
  <div class="hero" style="padding:38px 42px 34px">
    <div class="bdg">WALKTHROUGH · 源码走读</div>
    <h1>12 个程序，把整本书跑一遍</h1>
    <p>原书最值钱的部分是那些长例子：一个类从 20 行长到 200 行，每加一个方法就多一条规则。
    这里每个单元给一个完整程序——约 60–90 行、能直接跑、输出写在页面上，
    再逐段讲清楚「这行为什么这样写」。读完讲义跑一遍，比读三遍都牢。</p>
    <div class="st">
      <div><b>12</b><span>篇走读</span></div>
      <div><b>12</b><span>个可运行程序</span></div>
      <div><b>100%</b><span>输出实跑写回</span></div>
      <div><b>36</b><span>处改动练习</span></div>
    </div>
  </div>
  <div class="grid">{cards}</div>
  <p style="margin-top:26px;font-size:12.5px;color:var(--muted);line-height:1.9">
    每篇的代码块由 <code>tools/check_walk.py</code> 实跑通过，「运行输出」里的内容就是那一次的
    真实 stdout——不是手写的预期结果。改代码后重跑 <code>check_walk.py --write</code> 会自动更新。</p>
</div>"""
    out = page("源码走读 · 12 篇", body, where="lesson")
    open(os.path.join(WEB, "walk", "index.html"), "w", encoding="utf-8").write(out)
    return len(posts)

def main():
    os.makedirs(os.path.join(WEB, "css"), exist_ok=True)
    os.makedirs(os.path.join(WEB, "ch"), exist_ok=True)
    os.makedirs(os.path.join(WEB, "walk"), exist_ok=True)
    pyg = (_HF(style="monokai").get_style_defs(".main pre")
           + "\n" + _HF(style="monokai").get_style_defs(".wrap pre"))
    open(os.path.join(WEB, "css", "site.css"), "w", encoding="utf-8").write(
        CSS + "\n/* Pygments · monokai */\n" + pyg + "\n")
    units = load_units()
    if not units:
        raise SystemExit("course-fluent/ 下没有找到单元 md")
    import fluent_syllabus as _fs
    global SYL_TXT, SYL_RANGE
    _a, _b = _fs.totals(units)
    SYL_TXT = f"标准 {_a} 周 / 轻量 {_b} 周"
    SYL_RANGE = f"{_a}–{_b}"
    attach_cases(units, load_cases())
    build_units(units)
    build_lessons(units)
    build_bank(units)
    build_gates(units)
    build_deck(units)
    build_unit_decks(units)
    build_home(units)
    chars = build_coverage(units)
    terms = build_terms(units)
    rv = build_review(units)
    syl = build_syllabus(units)
    bn = build_bench(units)
    ds = build_design(units)
    wk = build_walk(units)
    print(f"正文 {chars:,} 字 | 术语 {terms} 条 | 复习排程 {rv} 课 × "
          f"{len(REVIEW_STAGES)} 轮 | 实测案例 {bn} 个 | 设计取舍 {ds} 章 | 源码走读 {wk} 篇 "
          f"| 总课表 {syl} 单元 × 2 种配速")
    print(f"单元 {len(units)} 个 | 课节 {sum(len(u['lessons']) for u in units)} 节")
    print(f"输出：{OUT}")

if __name__ == "__main__":
    main()
    import theme  # 主题派生：把浅色样式表翻成深色表并注入切换按钮
    theme.sweep([OUT])
