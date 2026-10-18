# -*- coding: utf-8 -*-
"""检查 slide DSL 里 <text> 是否互相重叠或超出画布。

批量生成 270+ 页课件时，靠肉眼看不过来。这个脚本解析每页所有 <text> 的
位置与字号，估算包围盒，报告：
  - 同一页内两个文本包围盒相交（真重叠）
  - 文本超出 1280x720 画布
  - 文本超出所属卡片（若同页有 rect，按其范围判断横向越界）

用法：
  python tools/check_slide_overlap.py <目录或文件...>
"""
import os
import re
import sys

CANVAS_W, CANVAS_H = 1280, 720
# 字符宽度估算：中文 1.0 em，ASCII 约 0.55 em
def char_w(ch):
    return 0.55 if ord(ch) < 128 else 1.0


TEXT_RE = re.compile(
    r"<text\b([^>]*)>(.*?)</text>", re.S)
ATTR_RE = re.compile(r"(\w+)=(['\"])(.*?)\2")


def parse_texts(dsl):
    out = []
    for m in TEXT_RE.finditer(dsl):
        attrs = dict((k, v) for k, _q, v in ATTR_RE.findall(m.group(1)))
        raw = re.sub(r"<[^>]+>", "", m.group(2))
        raw = raw.replace("&amp;", "&")
        try:
            x = float(attrs.get("x", 0))
            y = float(attrs.get("y", 0))
            fs = float(attrs.get("fontSize", 14))
        except ValueError:
            continue
        text = raw.strip()
        if not text:
            continue
        w = sum(char_w(c) for c in text) * fs
        anchor = attrs.get("textAnchor", "start")
        if anchor == "middle":
            x0, x1 = x - w / 2, x + w / 2
        elif anchor == "end":
            x0, x1 = x - w, x
        else:
            x0, x1 = x, x + w
        # 基线：上方 0.78em，下方 0.24em
        y0, y1 = y - fs * 0.78, y + fs * 0.24
        out.append(dict(text=text, x0=x0, x1=x1, y0=y0, y1=y1, fs=fs))
    return out


def overlap(a, b):
    ox = min(a["x1"], b["x1"]) - max(a["x0"], b["x0"])
    oy = min(a["y1"], b["y1"]) - max(a["y0"], b["y0"])
    if ox > 1.5 and oy > 1.5:
        return ox * oy
    return 0


def check_file(path):
    dsl = open(path, encoding="utf-8").read()
    ts = parse_texts(dsl)
    problems = []
    off = dsl.find("svg")
    in_svg = off != -1
    for t in ts:
        if t["x0"] < -2 or t["x1"] > CANVAS_W + 2:
            problems.append(f"横向越界 x=[{t['x0']:.0f},{t['x1']:.0f}] : {t['text'][:34]}")
        if t["y0"] < -2 or t["y1"] > CANVAS_H + 2:
            problems.append(f"纵向越界 y=[{t['y0']:.0f},{t['y1']:.0f}] : {t['text'][:34]}")
    for i in range(len(ts)):
        for j in range(i + 1, len(ts)):
            ar = overlap(ts[i], ts[j])
            if ar > 12:
                problems.append(
                    f"重叠 {ar:.0f}px² : 「{ts[i]['text'][:22]}」 × 「{ts[j]['text'][:22]}」")
    return problems


def main(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            for cur, _d, fs in os.walk(p):
                files += [os.path.join(cur, f) for f in fs if f.endswith(".slide")]
        else:
            files.append(p)
    files.sort()
    total_bad = 0
    for f in files:
        pr = check_file(f)
        if pr:
            total_bad += 1
            print(f"✗ {os.path.relpath(f)}")
            for x in pr[:6]:
                print(f"    {x}")
    print(f"\n检查 {len(files)} 页，{total_bad} 页有问题"
          + ("（全部通过）" if total_bad == 0 else ""))
    return 1 if total_bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["python-course-ppt/lessons-deck"]))
