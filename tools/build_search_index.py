"""生成 web/searchdata.js —— 全站搜索索引。

之前只有「课节索引页」能搜索，而且只搜标题/目标；111 节课 + 22 份讲义 +
52 道题，想找「字典 get」只能靠翻。这里把四类内容压成一个静态索引，
用 <script src> 引入（file:// 下 fetch 会被拦，script 不会）。

条目格式：[标题, 副标题, 链接, 关键词]
"""

import glob
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import build_lessons as BL      # noqa: E402
import lesson_tpl as LT         # noqa: E402
import ppt_map                  # noqa: E402
import bank_map                 # noqa: E402

OUT = os.path.join(ROOT, "web", "searchdata.js")


def js(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def strip_tags(t):
    return html.unescape(re.sub(r"<[^>]+>", "", t)).strip()


def lesson_entries():
    out = []
    for i, (u, _sl, wk, title, goal, live, hw) in enumerate(BL.LESSONS, 1):
        kw = " ".join([title, goal] + list(live) + list(hw))
        out.append([f"第 {i} 节 · {title}",
                    f"单元 {u} · {LT.UNIT_TITLE[u]} · {wk}",
                    f"lessons/{i:02d}.html",
                    kw])
    return out


def lecture_entries():
    """讲义页的 h2/h3 小节（带锚点）。"""
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "web", "[0-9][0-9].html"))):
        no = int(os.path.basename(f)[:2])
        s = open(f, encoding="utf-8").read()
        for m in re.finditer(r'<h([23]) id="([^"]+)"[^>]*>(.*?)</h\1>', s, re.S):
            txt = strip_tags(m.group(3))
            if not txt or txt == "---":
                continue
            txt = re.sub(r"\s+", " ", txt)[:60]
            out.append([f"单元 {no} · {txt}",
                        LT.UNIT_TITLE.get(no, ""),
                        f"{no:02d}.html#{m.group(2)}",
                        txt])
    return out


def bank_entries():
    out = []
    md = open(os.path.join(ROOT, "exercises", "题库-从入门到实践.md"),
              encoding="utf-8").read()
    for m in re.finditer(r"^## (L\d-\d+)[\s　]+(.+)$", md, flags=re.M):
        qid, title = m.group(1), m.group(2).strip()
        u = bank_map.UNIT_OF.get(qid)
        out.append([f"{qid} {title}",
                    f"练习 · 单元 {u} {LT.UNIT_TITLE.get(u, '')}".strip(),
                    f"bank.html#{qid}",
                    title])
    return out


def ppt_entries():
    out = []
    for i, s in enumerate(ppt_map.SLIDES, 1):
        title = s[0] if isinstance(s, (list, tuple)) else str(s)
        out.append([f"课件 p{i} · {title}", "课程大纲课件", f"ppt/index.html#s{i}", title])
    return out


def site_consts():
    """站点规模常量，从产物里数出来，避免页面里再写死 19+5 这类数字。"""
    import site_data
    gates = {}
    for n in (1, 2):
        f = os.path.join(ROOT, "web", f"gate{n}.html")
        gates[f"gate{n}"] = (open(f, encoding="utf-8").read().count("data-k=")
                             if os.path.exists(f) else 0)
    return {"units": site_data.unit_cnt(),
            "lessons": site_data.total_lessons(),
            "bank": site_data.question_cnt(),
            "slides": site_data.slide_cnt(),
            **gates}


def build():
    items = (lesson_entries() + lecture_entries()
             + bank_entries() + ppt_entries())
    lines = ",\n".join(
        "[" + ",".join(js(str(x)) for x in it) + "]" for it in items)
    import json as _json
    site = _json.dumps(site_consts(), ensure_ascii=False)
    data = ("/* 由 tools/build_search_index.py 生成，勿手改。\n"
            "   条目：[标题, 副标题, 链接(相对 web/), 关键词] */\n"
            "window.SITE=" + site + ";\n"
            "window.SEED=[\n" + lines + "\n];\n")
    open(OUT, "w", encoding="utf-8").write(data)
    return len(items), len(data)


if __name__ == "__main__":
    n, size = build()
    print(f"搜索索引：{n} 条，{size/1024:.1f} KB -> web/searchdata.js")
