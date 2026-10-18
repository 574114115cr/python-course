# -*- coding: utf-8 -*-
"""讲义结构体检：章节齐全 / 围栏配对 / 非对称缩进围栏 / 体量。

用法：
    python tools/check_lectures.py            # 检查 course/ 下全部
    python tools/check_lectures.py course/12-xxx.md ...
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FENCE = chr(96) * 3

# 每份讲义必须有的二级标题前缀
REQUIRED = ["一、学习目标", "二、核心知识点讲解", "三、可运行代码示例",
            "四、动手练习", "五、参考答案", "本单元小结与产出检查"]

# 体量区间（字符）。超出会告警——太小内容单薄，太大切课后单节课过重
MIN_BYTES, MAX_BYTES = 18_000, 190_000


def check(path):
    md = open(path, encoding="utf-8").read()
    lines = md.split("\n")
    problems = []

    # ── 围栏 ──
    fence_lines = [(i, ln) for i, ln in enumerate(lines) if ln.strip().startswith(FENCE)]
    if len(fence_lines) % 2:
        problems.append(f"围栏数为奇数（{len(fence_lines)}）——有代码块未闭合")

    # 非对称缩进围栏：开围栏缩进、闭围栏不缩进（或反之）是曾经搞坏单元 3 的元凶
    opens, closes = [], []
    inside = False
    for i, ln in fence_lines:
        indented = not ln.startswith(FENCE)
        if not inside:
            opens.append((i, indented))
            inside = True
        else:
            closes.append((i, indented))
            inside = False
    for (oi, oi_ind), (ci, ci_ind) in zip(opens, closes):
        if oi_ind != ci_ind:
            problems.append(
                f"第 {oi+1} 行开围栏缩进={oi_ind}，第 {ci+1} 行闭围栏缩进={ci_ind} —— "
                f"不对称，会让解析器把后面的标题吞进代码块")

    # ── 章节 ──
    hs, inside = [], False
    for ln in lines:
        if ln.strip().startswith(FENCE):
            inside = not inside
            continue
        if inside:
            continue
        g = re.match(r"^(#{1,4}) (.+)$", ln)
        if g:
            hs.append((len(g.group(1)), g.group(2).strip()))
    h2 = [t for lv, t in hs if lv == 2]
    for need in REQUIRED:
        if need == "本单元小结与产出检查":
            # 允许收尾章节的常见变体（不同单元用了不同的收尾名）
            ok = any(t.startswith("本单元小结") or "结业检查" in t or "小结与产出" in t
                     for t in h2)
            if not ok:
                problems.append("缺少收尾章节（本单元小结与产出检查 / 结业检查…）")
            continue
        if not any(t.startswith(need) for t in h2):
            problems.append(f"缺少二级标题「{need}」")

    # ── 体量 ──（按 UTF-8 字节算：中文 1 字 = 3 字节，用字符数会低估 3 倍）
    n = len(md.encode("utf-8"))
    if n < MIN_BYTES:
        problems.append(f"体量过小 {n//1024} KB（低于 {MIN_BYTES//1024} KB）——内容可能没写完")
    if n > MAX_BYTES:
        problems.append(f"体量过大 {n//1024} KB（高于 {MAX_BYTES//1024} KB）——切课后单节课会过重")

    return n, len(hs), problems   # n 是 UTF-8 字节数


def main():
    args = sys.argv[1:]
    if args:
        files = args
    else:
        files = sorted(os.path.join(ROOT, "course", f) for f in os.listdir(
            os.path.join(ROOT, "course")) if f.endswith(".md"))

    total_bad = 0
    print(f"{'讲义':<44}{'KB':>7}{'标题':>6}  问题")
    print("-" * 100)
    for f in files:
        n, nh, probs = check(f)
        flag = "OK" if not probs else f"{len(probs)} 个问题"
        print(f"{os.path.basename(f):<44}{n//1024:>7}{nh:>6}  {flag}")
        for p in probs:
            print(f"    ✗ {p}")
            total_bad += 1
    print("-" * 100)
    print(f"共 {len(files)} 份讲义，{total_bad} 个问题")
    return 1 if total_bad else 0


if __name__ == "__main__":
    sys.exit(main())
