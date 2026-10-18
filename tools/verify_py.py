# -*- coding: utf-8 -*-
"""校验讲义里每个 Python 代码块：语法必须合法（故意写错的教学块先豁免）。

分类口径：
  runnable  —— 纯 Python，通过 ast.parse
  broken    —— 标了 INTENTIONALLY-BROKEN 的故意写错教学块，不要求合法
  template  —— 含 Django 模板语法（{% %} / {{ }}）或 REPL 的 >>> 续行，不是纯 Python
  syntax    —— 真语法错误，必须报出来
"""
import ast
import glob
import os
import sys

FENCE = chr(96) * 3


def blocks(md):
    """返回 [(起始行号, info, 代码)]，只认顶格围栏。"""
    out, lines = [], md.split("\n")
    inside, start, info, buf = False, 0, "", []
    for i, ln in enumerate(lines):
        if ln.startswith(FENCE):
            if not inside:
                inside, start, info, buf = True, i, ln[3:].strip(), []
            else:
                out.append((start + 1, info, "\n".join(buf)))
                inside = False
            continue
        if inside:
            buf.append(ln)
    return out


def classify(code, info):
    lang = info.split()[0].lower() if info else ""
    if lang and lang != "python":
        return "other", None
    if not code.strip():
        return "other", None
    if lang == "":
        # 无语言标注的裸围栏：按内容猜。和 build_lectures.py 的启发式保持一致。
        import re
        if re.search(r"Traceback \(most recent call last\)|File \".*\", line \d+"
                     r"|^\w*(Error|Exception):", code, re.M):
            return "other", None                       # traceback 输出
        if re.search(r"├──|└──|│|┌|└|—|×", code):
            return "other", None                       # ASCII 树 / 图
        if re.search(r"^\s*={3,}.*={3,}\s*$|PASSED|FAILED|collected \d+ items",
                     code, re.M):
            return "other", None                       # pytest 报告
        if re.search(r"^\s*(from|import |def |class |for |while |if |print\()",
                     code, re.M):
            lang = "python"                            # 确实是 Python
        else:
            return "other", None                       # 中文注解 / 伪代码 / 命令行
    if any("INTENTIONALLY-BROKEN" in ln for ln in code.split("\n")[:3]):
        return "broken", None
    if "{% " in code or "{{ " in code:      # Django 模板
        return "template", None
    if code.lstrip().startswith(">>> ") or "\n>>> " in code:
        return "template", None
    try:
        ast.parse(code)
        return "runnable", None
    except SyntaxError as e:
        return "syntax", f"第 {e.lineno} 行: {e.msg}"


def main(paths):
    stats = {"runnable": 0, "broken": 0, "template": 0, "syntax": 0, "other": 0}
    errs = []
    for p in paths:
        md = open(p, encoding="utf-8").read()
        for lineno, info, code in blocks(md):
            kind, msg = classify(code, info)
            stats[kind] += 1
            if kind == "syntax":
                errs.append((os.path.basename(p), lineno, info, msg))

    print(f"扫描 {len(paths)} 份讲义：")
    print(f"  可运行 Python  {stats['runnable']:>4}")
    print(f"  故意写错教学块  {stats['broken']:>4}（豁免）")
    print(f"  模板 / REPL     {stats['template']:>4}（非纯 Python）")
    print(f"  其他语言        {stats['other']:>4}（bash / html / text 等）")
    print(f"  ★ 语法错误      {stats['syntax']:>4}")
    for f, ln, info, msg in errs:
        print(f"    ✗ {f}:{ln} [{info or 'python'}] {msg}")
    return 1 if stats["syntax"] else 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if args:
        files = args
    else:
        files = sorted(glob.glob(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "course", "*.md")))
    sys.exit(main(files))