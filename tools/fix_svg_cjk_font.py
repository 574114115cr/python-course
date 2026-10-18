# -*- coding: utf-8 -*-
"""修复 SVG <text> 的中文豆腐块问题。

实验结论（见 _exp/t.slide 的对照渲染）：
  渲染器的默认 SVG 字体**不含中文字形**，无论是否写 fontFamily='Inter'、
  无论文本是否以中文开头，含中文的 <text> 都会渲染成「□□」。
  唯一有效的做法是显式指定一个含中文字形的字体。

修复策略：对含中日韩字符的 <text>，把 fontFamily 统一设为中文字体；
纯拉丁文本保持不动（保留 Inter，不影响设计语言）。
"""
import os
import re
import sys

CJK = re.compile(r'[\u3000-\u303f\u4e00-\u9fff\uff00-\uffef\u2018\u2019\u201c\u201d]')
CJK_FONT = "Microsoft YaHei"

DEFAULT_DIR = ("python-course-ppt", "slides", "deck2")


def fix_tag(m):
    tag = m.group(0)
    inner = re.sub(r'<[^>]+>', '', tag)
    if not CJK.search(inner):
        return tag                                  # 纯拉丁：不动

    # 已有 fontFamily → 换成中文字体；没有 → 追加
    if re.search(r"fontFamily=(?:'[^']*'|\"[^\"]*\")", tag):
        tag = re.sub(r"fontFamily=(?:'[^']*'|\"[^\"]*\")",
                     f"fontFamily='{CJK_FONT}'", tag)
    else:
        tag = re.sub(r'^<text\b', f"<text fontFamily='{CJK_FONT}'", tag)
    return tag


def main(paths):
    files = changed = 0
    for p in paths:
        s = open(p, encoding="utf-8").read()
        new = re.sub(r'<text\b[^>]*>.*?</text>', fix_tag, s, flags=re.S)
        if new != s:
            open(p, "w", encoding="utf-8").write(new)
            changed += 1
        files += 1
    print(f"扫描 {files} 个文件，修改 {changed} 个")
    # 复查：还有没有含中文却没用中文字体的 <text>
    left = []
    for p in paths:
        s = open(p, encoding="utf-8").read()
        for m in re.finditer(r'<text\b[^>]*>.*?</text>', s, re.S):
            tag = m.group(0)
            inner = re.sub(r'<[^>]+>', '', tag)
            if CJK.search(inner) and CJK_FONT not in tag:
                left.append((os.path.basename(p), inner[:30]))
    print("残留问题：", len(left))
    for f, t in left[:10]:
        print("   ", f, t)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args:
        files = args
    else:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        d = os.path.join(root, *DEFAULT_DIR)
        files = [os.path.join(d, f) for f in sorted(os.listdir(d))]
    main(files)
