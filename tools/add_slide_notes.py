"""给逐节版课件补「演讲者备注」。

slidep 的 DSL 不支持 notes（bundle 里没有这个字段，validate 也不认），
所以用 python-pptx 在生成后补写：每页备注写清「这一页讲什么、时间怎么分配、
学生容易卡在哪」，讲课时不用再翻讲义。

用法：python tools/add_slide_notes.py
"""

import json
import os
import sys

from lxml import etree
from pptx import Presentation
from pptx.oxml.ns import nsdecls
from pptx.util import Emu

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import build_lessons as BL            # noqa: E402
import lesson_tpl as LT               # noqa: E402

DECK = os.path.join(ROOT, "python-course-ppt", "逐节课件")
MANI = os.path.join(ROOT, "python-course-ppt", "lessons-deck", "manifest.json")

RHYTHM = ("节奏：讲 20 分钟 → 学员自己敲 40 分钟（不看答案）→ 对讲评自查 20 分钟 "
          "→ 写作业 10 分钟。")


def lesson_notes(no):
    u, _sl, wk, title, goal, live, hw = BL.LESSONS[no - 1]
    body = [f"第 {no} 节 · {title}",
            f"单元 {u} · {LT.UNIT_TITLE[u]} · {wk}",
            "",
            f"学习目标：{goal}",
            "",
            "课堂实操（40 分钟，不看答案）："]
    body += [f"· {x}" for x in live]
    body.append("")
    body.append("课后作业：")
    body += [f"· {x}" for x in hw]
    body += ["", RHYTHM]
    return "\n".join(body)


def points_notes(no):
    u, _sl, wk, title, goal, live, hw = BL.LESSONS[no - 1]
    return "\n".join([
        f"第 {no} 节 · 核心知识点：{title}",
        "",
        "讲这一页时：先让学生说出上节课的结论，再逐块讲要点。",
        "每讲完一块，问一句「这一步如果写错了，报错会长什么样？」——把错误提前讲。",
        "",
        f"本节目标：{goal}",
        "",
        "看不到懂的地方，回讲义对应小节读一遍，再回来对着这页复述一次——能讲出来才算真懂。",
    ])


def cover_notes(u, title, lessons):
    lines = [f"单元 {u} · {title}", "", "本单元包含以下课节："]
    lines += [f"· 第 {n} 节 {t}" for n, t in lessons]
    lines += ["", "开场用 3 分钟讲清：这个单元学完能做出什么，最后会被关卡怎么验。"]
    return "\n".join(lines)


def summary_notes(u, title):
    return "\n".join([
        f"单元 {u} 小结 · {title}",
        "",
        "收尾动作：让学生合上讲义，口述本单元三个最重要的结论；说不出来的，回对应课节。",
        "然后当场勾一遍本单元课节的「已完成」，没打勾的进下一单元前补掉。",
    ])


def put_notes(slide, text):
    """把备注写进备注页。

    起因：slidep 生成的 pptx 里 notesMaster 的 spTree 是空的（没有 body 占位符），
    所以 python-pptx 的 `slide.notes_slide.notes_text_frame` 返回 None，无法直接赋值。
    这里绕过去：往备注页 spTree 里插一个文本框（PowerPoint 的备注视图能正常显示）。
    """
    ns = slide.notes_slide
    tree = ns.shapes._spTree
    # 重跑时就地更新已有文本框，避免越叠越多
    for old in tree.findall("{%s}sp" % nsdecls("p")[3:-1]):
        tree.remove(old)

    id_ = 2
    ps = []
    for line in text.split("\n"):
        esc = (line.replace("&", "&amp;").replace("<", "&lt;")
                   .replace(">", "&gt;"))
        ps.append(f'<a:p><a:r><a:rPr lang="zh-CN" dirty="0"/>'
                  f'<a:t>{esc}</a:t></a:r></a:p>')
    xml = (
        f'<p:sp {nsdecls("p", "a")}>'
        f'<p:nvSpPr><p:cNvPr id="{id_}" name="讲课提示"/>'
        f'<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="457200" y="457200"/>'
        f'<a:ext cx="6858000" cy="4800600"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
        f'<p:txBody><a:bodyPr wrap="square"/><a:lstStyle/>'
        + "".join(ps) +
        f'</p:txBody></p:sp>')
    tree.append(etree.fromstring(xml))


def annotate(src, dst, unit, meta):
    """给 src 补备注，另存为 dst（不碰 src）。

    为什么要能「另存」：这个环境里每个文件每会话只允许写一次——pptx 一旦被写，
    立刻被别的进程占住（读得出、写不进）。所以备注必须和 pptx 的创建合并成
    一次写入：build_all_lesson_ppt 先建临时 deck，这里补好备注，再整体写回正式文件。
    """
    prs = Presentation(src)
    if len(prs.slides) != len(meta):
        raise ValueError(f"页数不一致：pptx {len(prs.slides)} vs 清单 {len(meta)}")
    lessons = [(m["no"], m["title"]) for m in meta if m["kind"] == "lesson"]
    for slide, m in zip(prs.slides, meta):
        if m["kind"] == "cover":
            txt = cover_notes(unit, m["title"], lessons)
        elif m["kind"] == "lesson":
            txt = lesson_notes(m["no"])
        elif m["kind"] == "points":
            txt = points_notes(m["no"])
        else:
            txt = summary_notes(unit, m["title"])
        put_notes(slide, txt)
    prs.save(dst)
    return len(meta)


def main():
    mani = json.load(open(MANI, encoding="utf-8"))
    total = 0
    failed = []
    for u in range(22):
        f = os.path.join(DECK, f"Python讲授课件-单元{u:02d}.pptx")
        if not os.path.exists(f):
            print(f"  单元{u:02d} 课件缺失，跳过")
            continue
        prs = Presentation(f)
        meta = mani[str(u)]
        if len(prs.slides) != len(meta):
            print(f"  !! 单元{u:02d} 页数不一致：pptx {len(prs.slides)} vs 清单 {len(meta)}")
        lessons = [(m["no"], m["title"]) for m in meta if m["kind"] == "lesson"]
        for slide, m in zip(prs.slides, meta):
            if m["kind"] == "cover":
                txt = cover_notes(u, m["title"], lessons)
            elif m["kind"] == "lesson":
                txt = lesson_notes(m["no"])
            elif m["kind"] == "points":
                txt = points_notes(m["no"])
            else:
                txt = summary_notes(u, m["title"])
            put_notes(slide, txt)
            total += 1
        try:
            prs.save(f)
        except (PermissionError, OSError) as error:
            # 文件被别的进程占着时不要整份脚本罢工：其余单元照样补备注。
            # 踩过：以前这里直接抛异常，结果 22 个单元一个都没写进去。
            failed.append(u)
            print(f"  单元{u:02d}: 写不进（{type(error).__name__}），跳过备注")
            continue
        print(f"  单元{u:02d}: {len(meta)} 页备注已写")
    print(f"合计 {total} 页备注")
    if failed:
        print(f"!! 有 {len(failed)} 个单元备注没写进去（文件被占用）：{failed}")
        print("   这些单元页面/图片都正常，只缺演讲者备注，解锁后重跑本脚本即可。")


if __name__ == "__main__":
    main()
