"""走读审计：结构、章节对应、产物完整性（配合 check_walk.py 的实跑校验）。

    python tools/audit_walk.py

检查项：
  [1] 12 篇齐全，首行 @@uNN|标题，标题非空
  [2] 固定小节：程序 / 逐段走读 / 运行输出 / 跑通之后改三处 / 对应原书哪里
  [3] 「运行输出」不是占位符（已写回实跑结果）、不含 Traceback
  [4] 产物 fluent/web/walk/uNN.html 存在，含 pre.out、返回单元页的链接
  [5] 走读总览页列出 12 篇
  [6] 单元页侧栏与本单元课节的「走读」入口存在
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "course-fluent", "walk")
WEB = os.path.join(ROOT, "fluent", "web", "walk")
SECTIONS = ["## 程序", "## 逐段走读", "## 运行输出", "## 跑通之后改三处", "## 对应原书哪里"]

bad = []
lines = []
for no in range(1, 13):
    fn = os.path.join(SRC, f"u{no:02d}.md")
    if not os.path.exists(fn):
        bad.append(f"缺少源文件 u{no:02d}.md")
        continue
    md = open(fn, encoding="utf-8").read()
    h = re.match(r"@@u(\d{2})\|(.+)", md)
    if not h or int(h.group(1)) != no:
        bad.append(f"u{no:02d}.md 首行不是「@@u{no:02d}|标题」")
    for sec in SECTIONS:
        if sec not in md:
            bad.append(f"u{no:02d}.md 缺少小节「{sec[3:]}」")
    out = re.search(r"## 运行输出\s*\n+```text\n(.*?)\n```", md, re.S)
    if not out:
        bad.append(f"u{no:02d}.md 运行输出块缺失或格式不对")
    else:
        body = out.group(1)
        if "@@OUT@@" in body or not body.strip():
            bad.append(f"u{no:02d}.md 运行输出还是占位符")
        if "Traceback" in body:
            bad.append(f"u{no:02d}.md 运行输出里有 Traceback")
    code = re.search(r"```python\n(.*?)```", md, re.S)
    n_lines = len(code.group(1).splitlines()) if code else 0
    if not 40 <= n_lines <= 130:
        bad.append(f"u{no:02d}.md 代码 {n_lines} 行，超出 40–130 的合理区间")
    # 产物
    page = os.path.join(WEB, f"u{no:02d}.html")
    if not os.path.exists(page):
        bad.append(f"缺少产物 walk/u{no:02d}.html")
    else:
        s = open(page, encoding="utf-8").read()
        if 'class="out"' not in s:
            bad.append(f"u{no:02d}.html 里没有运行输出块（pre.out）")
        if f'../{no:02d}.html' not in s:
            bad.append(f"u{no:02d}.html 缺少回单元 {no} 讲义的链接")
    lines.append(f"u{no:02d} · {h.group(2) if h else '?'} | 代码 {n_lines} 行 | "
                 f"输出 {len(out.group(1).splitlines()) if out else 0} 行")

idx = os.path.join(WEB, "index.html")
if not os.path.exists(idx):
    bad.append("缺少走读总览 walk/index.html")
else:
    s = open(idx, encoding="utf-8").read()
    n_link = len(re.findall(r'href="u\d{2}\.html"', s))
    if n_link != 12:
        bad.append(f"总览页列出 {n_link} 篇，应为 12 篇")

# 入口：12 个单元页 + 48 个课节页都要有走读链接
for no in range(1, 13):
    u = os.path.join(ROOT, "fluent", "web", f"{no:02d}.html")
    if os.path.exists(u) and f"walk/u{no:02d}.html" not in open(u, encoding="utf-8").read():
        bad.append(f"单元 {no} 页缺少走读入口")
    for local in range(1, 5):
        g = (no - 1) * 4 + local
        p = os.path.join(ROOT, "fluent", "web", "lessons", f"l{g:02d}.html")
        if os.path.exists(p) and f"../walk/u{no:02d}.html" not in open(p, encoding="utf-8").read():
            bad.append(f"第 {g} 课页面缺少走读入口")

print("\n".join(lines))
print()
if bad:
    print(f"✗ {len(bad)} 个问题：")
    for b in bad:
        print("  -", b)
    sys.exit(1)
print("✓ 走读审计通过：12 篇结构完整、输出已写回、入口 12+48 处齐备")
