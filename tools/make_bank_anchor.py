# -*- coding: utf-8 -*-
"""给题库的每道题标一个「回看哪个小节」的锚点。

为什么单独一步：题库只到「单元级」（`data-u`），学习者做错题要回到讲义时，
还得自己在目录里找「这道题到底考的是 2.5 还是 3.2」。有了锚点，卡片右上角那条
「单元 N」直接跳到对应小节。

做法（不手工标注 120 条）：
  1. 从**已生成的单元页**里取真实的小节锚点（`<h3 id="2-5-...">`），
     不自己复现 slug 规则——复现一遍迟早和页面不一致；
  2. 用「小节标题里的词」与「题干 + 答案解析」做关键词重合度打分，取最高分；
  3. 分数不够就**不猜**，返回 None（卡片退回链到单元页），并把统计打出来。

产物 `tools/bank_anchor.json`：{题号: 锚点或 null}。可以手改，改完重跑构建即可。
用法：python tools/make_bank_anchor.py [--write]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import bank_map  # noqa: E402

WEB = os.path.join(ROOT, "web")
MD = os.path.join(ROOT, "exercises", "题库-从入门到实践.md")
OUT = os.path.join(HERE, "bank_anchor.json")

# 只保留有信息量的词：去掉纯数字编号、单字、常见虚词
STOP = set("的 了 和 与 或 是 在 有 时 也 就 都 而 及 用 一个 什么 怎么 为 对 把 被 让 从 到 "
           "写法 做法 例子 情况 问题 时候 下面 上面 这里 那里 我们 你 他 它 这 那".split())


# 人工标注：题号 → 该单元的小节编号（"2.5" 这种）。
# 自动关键词匹配只有 56%，而且 46 条是弱匹配——会把人带到不相干的小节，
# 比不标更糟。所以改成按题目内容逐条指定，脚本负责校验锚点在页面上真的存在。
MANUAL = {
    # 单元 0
    "L1-10": "0.2.3",   # PEP 8 格式化 → VS Code 配置
    # 单元 1
    "L1-1": "1.2.1", "L1-2": "1.2.7", "L1-3": "1.2.3", "L1-7": "1.2.4",
    "L1-11": "1.2.4", "L1-13": "1.2.7", "L1-14": "1.2.7",
    # 单元 2
    "L1-4": "2.2.1", "L1-5": "2.2.2", "L1-6": "2.2.3", "L1-8": "2.2.4",
    "L1-15": "2.2.3", "L1-16": "2.2.6",
    # 单元 3
    "L2-1": "3.2.1", "L2-2": "3.2.2", "L2-3": "3.2.4", "L2-4": "3.2.3",
    "L2-5": "3.2.5", "L2-13": "3.2.3", "L2-15": "3.2.3", "L2-17": "3.2.5",
    "L2-18": "3.2.5",
    # 单元 4
    "L1-9": "4.2.1", "L2-6": "4.2.3", "L2-7": "4.2.4", "L2-8": "4.2.2",
    "L2-19": "4.2.3", "L2-20": "4.2.2",
    # 单元 5
    "L2-16": "5.2.2", "L2-21": "5.2.7", "L2-22": "5.2.7",
    # 单元 6
    "L1-12": "6.2.6", "L2-9": "6.2.3", "L2-10": "6.2.4", "L2-11": "6.2.7",
    "L2-12": "6.2.6", "L2-14": "6.2.5", "L2-23": "6.2.7", "L2-24": "6.2.7",
    # 单元 7
    "L3-1": "7.2.3", "L3-2": "7.2.2", "L3-3": "7.2.4", "L3-4": "7.2.3",
    "L3-5": "7.2.7", "L3-6": "7.2.2", "L3-7": "7.2.6", "L3-8": "7.2.1",
    "L3-9": "7.2.7", "L3-10": "7.2.7",
    # 单元 8
    "L4-1": "8.2.1", "L4-2": "8.2.3", "L4-3": "8.2.4", "L4-4": "8.2.6",
    "L4-5": "8.2.7", "L4-6": "8.2.6", "L4-7": "8.2.6", "L4-8": "8.2.8",
    "L4-9": "8.2.8", "L4-10": "8.2.8",
    # 单元 9
    "L5-1": "9.2.5", "L5-2": "9.2.3", "L5-3": "9.2.6", "L5-4": "9.2.7",
    "L5-5": "9.2.8", "L5-6": "9.2.8",
    # 单元 10
    "L5-7": "10.2.3", "L5-8": "10.2.6",
    # 单元 11
    "L5-9": "11.2.3", "L5-10": "11.2.3",
    # 单元 12
    "L6-1": "12.2.4", "L6-2": "12.2.5", "L6-3": "12.2.7",
    "L6-31": "12.2.8", "L6-32": "12.2.6",
    # 单元 13
    "L6-4": "13.2.3", "L6-5": "13.2.2", "L6-6": "13.2.5", "L6-7": "13.2.7",
    "L6-33": "13.2.7", "L6-34": "13.2.6",
    # 单元 14
    "L6-8": "14.2.2", "L6-9": "14.2.4", "L6-10": "14.2.6",
    "L6-35": "14.2.5", "L6-36": "14.2.4",
    # 单元 15
    "L6-11": "15.2.3", "L6-12": "15.2.4", "L6-13": "15.2.5",
    "L6-37": "15.2.6", "L6-38": "15.2.7",
    # 单元 16
    "L6-14": "16.2.2", "L6-15": "16.2.6", "L6-16": "16.2.3",
    "L6-39": "16.2.2", "L6-40": "16.2.6",
    # 单元 17
    "L6-17": "17.2.4", "L6-18": "17.2.5", "L6-19": "17.2.5", "L6-20": "17.2.5",
    "L6-41": "17.2.3", "L6-42": "17.2.4",
    # 单元 18
    "L6-21": "18.2.5", "L6-22": "18.2.7", "L6-23": "18.2.3",
    "L6-43": "18.2.5", "L6-44": "18.2.6",
    # 单元 19
    "L6-24": "19.2.4", "L6-25": "19.2.5", "L6-45": "19.2.6", "L6-46": "19.2.1",
    # 单元 20
    "L6-26": "20.2.2", "L6-27": "20.2.7", "L6-47": "20.2.7", "L6-48": "20.2.5",
    # 单元 21
    "L6-28": "21.2.1", "L6-29": "21.2.1", "L6-30": "21.2.4",
    "L6-49": "21.2.2", "L6-50": "21.2.2",
}


def tokens(text):
    """把标题/正文切成可用于比对的词：中文二元片段 + ASCII 标识符。"""
    text = re.sub(r"`[^`]*`", lambda m: " " + m.group(0).strip("`") + " ", text)
    parts = re.split(r"[^0-9A-Za-z_\u4e00-\u9fff]+", text)
    out = []
    for p in parts:
        p = p.strip()
        if not p or p in STOP:
            continue
        if len(p) <= 1:
            continue
        out.append(p.lower())
    return out


def unit_sections(unit):
    """从已生成的单元页里取 (锚点, 小节标题) 列表。"""
    path = os.path.join(WEB, f"{unit:02d}.html")
    if not os.path.exists(path):
        return []
    html = open(path, encoding="utf-8").read()
    out = []
    for m in re.finditer(r'<h([23]) id="([^"]+)"[^>]*>(.*?)</h\1>', html, re.S):
        text = re.sub(r"<[^>]+>", "", m.group(3))
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            out.append((m.group(2), text))
    return out


def parse_questions():
    md = open(MD, encoding="utf-8").read()
    qs = {}
    for m in re.finditer(r"^## (L\d-\d+) (.+?)$(.*?)(?=^## L\d-\d+ |\Z)",
                         md, re.S | re.M):
        qs[m.group(1)] = m.group(0)
    return qs


def score(sec_title, qtext):
    """小节标题里的词在题干/答案里出现了几个（长的词权重更高）。"""
    tk = tokens(sec_title)
    if not tk:
        return 0.0
    hit = sum(len(t) for t in tk if t in qtext)
    total = sum(len(t) for t in tk)
    return hit / total if total else 0.0


def main():
    write = "--write" in sys.argv
    qs = parse_questions()
    sec_cache = {}
    result, missing, bad = {}, [], []

    for qid in qs:
        unit = bank_map.UNIT_OF.get(qid)
        label = MANUAL.get(qid)
        if unit is None or not label:
            result[qid] = None
            missing.append(qid)
            continue
        if unit not in sec_cache:
            sec_cache[unit] = unit_sections(unit)
        # label 形如 "12.2.8"：第一段是单元号，后面是 2.x 的小节号
        parts = label.split(".")
        want = f"{parts[1]}-{parts[2]}-"          # 例如 "2-8-"
        hit = next((a for a, _t in sec_cache[unit] if a.startswith(want)), None)
        if hit is None:
            bad.append((qid, label))
            result[qid] = None
        else:
            result[qid] = hit

    total = len(qs)
    ok = sum(1 for v in result.values() if v)
    print(f"题目 {total} 道：已定位 {ok}，未标注 {total - ok}")
    if missing:
        print(f"  未标注：{missing}")
    if bad:
        print(f"  !! 标注的锚点在页面上不存在（检查小节号）：{bad}")
        return 1
    if write:
        json.dump(result, open(OUT, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1, sort_keys=True)
        print(f"已写入 {os.path.relpath(OUT, ROOT)}")
    else:
        print("（未写文件，加 --write 生效）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
