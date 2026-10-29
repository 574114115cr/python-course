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
SITE_OUT = os.path.join(ROOT, "web", "site.js")


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


def review_entries():
    """复习计划页：艾宾浩斯排程入口。"""
    return [["复习计划 · 艾宾浩斯遗忘曲线",
             "6 轮间隔重复 · 今日待复习 / 逾期 / 记忆保持率",
             "review.html",
             "复习 遗忘曲线 艾宾浩斯 间隔重复 复习计划 记忆保持率"]]


def index_entries():
    """术语索引 + 覆盖矩阵：入门课补齐的两张检索页。"""
    return [
        ["术语索引 · 正文标识符",
         "按字母分组 · 每条给课号直达 · 替代教材末尾索引",
         "terms.html",
         "术语 索引 查函数 查方法 append input sorted __init__ 关键字 速查"],
        ["覆盖与自足性 · 教材 20 章 + 附录 A–E",
         "逐章对照 / 附录讲到什么程度 / 多出来的 / 不替代的部分",
         "coverage.html",
         "覆盖 对照 教材章节 附录 自足 不替代 完整性 大纲 进度 目录"],
    ]


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
             + bank_entries() + ppt_entries() + review_entries()
             + index_entries())
    lines = ",\n".join(
        "[" + ",".join(js(str(x)) for x in it) + "]" for it in items)
    import json as _json
    site = _json.dumps(site_consts(), ensure_ascii=False)
    # 拆成两个文件：
    #   site.js  —— 只有规模数字（几百字节），每页同步加载，页面上的数量靠它；
    #   searchdata.js —— 整个搜索索引（160+ KB），首页**首次聚焦搜索框才加载**。
    # 以前合成一个同步 <script>，首页要等 166 KB 下载+解析完才能继续，
    # 而是这些字节对「不搜索的人」完全没用。
    site_js = ("/* 由 tools/build_search_index.py 生成，勿手改。 */\n"
               "window.SITE=" + site + ";\n")
    open(SITE_OUT, "w", encoding="utf-8").write(site_js)

    data = ("/* 由 tools/build_search_index.py 生成，勿手改。\n"
            "   条目：[标题, 副标题, 链接(相对 web/), 关键词] */\n"
            "window.SEED=[\n" + lines + "\n];\n")
    open(OUT, "w", encoding="utf-8").write(data)
    print(f"  site.js {len(site_js)//1024} KB（同步）/ "
          f"searchdata.js {len(data)//1024} KB（懒加载）")
    return len(items), len(data)


if __name__ == "__main__":
    n, size = build()
    print(f"搜索索引：{n} 条，{size/1024:.1f} KB -> web/searchdata.js")
