# -*- coding: utf-8 -*-
"""生成逐节版课件的总览页：web/ppt/u/index.html

22 张卡片，每张一个单元的封面缩略图 + 课节数，点进去是该单元的课件播放器。
"""
import importlib.util
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
WEB_U = os.path.join(ROOT, "web", "ppt", "u")


def load(name, rel):
    sp = importlib.util.spec_from_file_location(name, os.path.join(TOOLS, rel))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def main():
    lt = load("lt", "lesson_tpl.py")
    manifest = json.load(open(os.path.join(ROOT, "python-course-ppt",
                                           "lessons-deck", "manifest.json"),
                              encoding="utf-8"))

    cards = []
    for u in sorted(int(k) for k in manifest):
        slides = manifest[str(u)]
        n_lesson = sum(1 for s in slides if s["kind"] == "lesson")
        n_slide = len(slides)
        stage = 1 if u <= 11 else 2
        color = "#1F5FA8" if stage == 1 else "#0E9B78"
        title = lt.UNIT_TITLE.get(u, "")
        cards.append(f"""
    <a class="c" href="{u:02d}.html">
      <img loading="lazy" src="{u:02d}/slide-01.webp" alt="单元 {u} 封面">
      <div class="cb">
        <div class="ch"><span class="cn" style="background:{color}">单元 {u}</span>
          <span class="cm">{n_lesson} 节 · {n_slide} 页</span></div>
        <h3>{title}</h3>
      </div>
    </a>""")

    html = TEMPLATE.replace("__CARDS__", "".join(cards))
    out = os.path.join(WEB_U, "index.html")
    open(out, "w", encoding="utf-8").write(html)
    print(f"生成 {out}（{len(cards)} 个单元）")


TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>逐节版讲授课件 · 22 个单元</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 32 32\'%3E%3Crect width=\'32\' height=\'32\' rx=\'7\' fill=\'%231f5fa8\'/%3E%3Ctext x=\'16\' y=\'22\' font-size=\'15\' font-family=\'monospace\' fill=\'%23fff\' text-anchor=\'middle\'%3EPy%3C/text%3E%3C/svg%3E">
<style>
:root{--bg:#eef2f7;--card:#fff;--line:#d8e3ee;--text:#16232e;--muted:#5f7183;
--p1:#1f5fa8;--p2:#0e9b78;--p3:#e08a15}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);line-height:1.7;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif}
a{color:inherit;text-decoration:none}
.top{background:var(--card);border-bottom:1px solid var(--line)}
.top-in{max-width:1180px;margin:0 auto;padding:14px 22px;display:flex;
align-items:center;gap:12px;flex-wrap:wrap}
.brand{font-size:17px;font-weight:700}
.spacer{flex:1}
.btn{font-size:13.5px;border:1px solid var(--line);background:#fff;color:var(--p1);
border-radius:8px;padding:7px 13px;font-weight:600}
.btn:hover{background:#f2f7fd}
.wrap{max-width:1180px;margin:0 auto;padding:24px 22px 60px}
h1{font-size:26px;margin:4px 0 6px}
.sub{color:var(--muted);font-size:15px;margin:0 0 22px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:16px}
.c{background:var(--card);border:1px solid var(--line);border-radius:14px;
overflow:hidden;transition:transform .12s,box-shadow .12s,border-color .12s}
.c:hover{transform:translateY(-3px);border-color:var(--p1);
box-shadow:0 6px 20px rgba(31,95,168,.12)}
.c img{display:block;width:100%;height:auto;border-bottom:1px solid var(--line)}
.cb{padding:13px 16px 16px}
.ch{display:flex;align-items:center;gap:9px;margin-bottom:5px}
.cn{font-size:12px;font-weight:700;color:#fff;border-radius:5px;padding:2px 9px}
.cm{font-size:12.5px;color:var(--muted);margin-left:auto}
.cb h3{margin:0;font-size:16px;color:var(--text)}
.note{background:#fff;border:1px solid var(--line);border-left:4px solid var(--p3);
border-radius:10px;padding:15px 18px;margin-bottom:22px;font-size:14.5px;color:#3a4a58}
.note b{color:var(--p3)}
</style>
</head>
<body>
<div class="top"><div class="top-in">
  <span class="brand">逐节版讲授课件</span>
  <span class="spacer"></span>
  <a class="btn" href="../../lessons/index.html">按课节学</a>
  <a class="btn" href="../index.html">课程大纲课件</a>
  <a class="btn" href="../../../index.html">课程主页</a>
</div></div>
<div class="wrap">
  <h1>逐节版讲授课件 · 22 个单元</h1>
  <p class="sub">每个单元一份，<b>每一节课都有两页</b>：课节页（学习目标 / 课堂实操 / 课后作业）
     与知识点页（本节要点 + 代码示例）。讲哪一节就翻哪两页，不用再从大纲里找。</p>
  <div class="note"><b>怎么找本课节的页？</b>点进任意一个单元，或用课节页右上角的
     <b>「本课课件」</b>按钮——它会直接跳到那一节自己的两页。</div>
  <div class="grid">__CARDS__</div>
</div>
<script src="../../media/bgm.js" defer></script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
