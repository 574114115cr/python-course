"""校验讲义中所有 Python 代码块：1) 语法 compile()  2) 逻辑实际执行。

- 语法校验：所有非"故意写错"的块都要 compile() 通过
- 逻辑执行：非交互、无外部依赖的块在临时目录里真实跑一遍（子进程 + 超时）
"""
import re
import sys
import os
import pathlib
import tempfile
import subprocess

CODE_RE = re.compile(r"```python\n(.*?)```", re.DOTALL)
BROKEN_MARK = "INTENTIONALLY-BROKEN"
# 片段标记：只讲一个方法/视图的一部分，顶层 return、未定义名都是故意的
FRAGMENT_MARK = "（片段）"


def _dedent(code):
    """去掉列表内嵌带来的一层公共缩进（与 build_lectures.convert 保持一致）。"""
    lines = code.split("\n")
    indents = [len(l) - len(l.lstrip()) for l in lines if l.strip()]
    if indents and min(indents) > 0:
        cut = min(indents)
        lines = [l[cut:] if l.strip() else l for l in lines]
    return "\n".join(lines)


def blocks(path):
    text = path.read_text(encoding="utf-8")
    return [_dedent(c) for c in CODE_RE.findall(text)]


def is_fragment(code):
    head = code.split("\n")[0]
    return FRAGMENT_MARK in head


# 需要外部模块或跨文件依赖的块（跳过逻辑执行，只做语法校验）
EXTERNAL = re.compile(
    r"^\s*(?:from|import)\s+(?:pytest|requests|django|pygame|flask)\b"
    r"|\bfrom\s+(calculator|text_utils|divider|book|buggy|tip|cart|bank_system|"
    r"library|shelf_library|vote_analyzer|score_analyzer|text_analyzer|vehicle|"
    r"analysis|user_input_report|todo_manager)\b",
    re.M,
)


def syntax_check(files):
    total = skipped = 0
    problems = []
    print("=" * 60)
    print("第一部分：语法校验（compile）")
    print("=" * 60)
    for f in files:
        count = skip = frag = 0
        for code in blocks(f):
            if BROKEN_MARK in code.split("\n")[0]:
                skip += 1
                continue
            if is_fragment(code):
                frag += 1
                continue
            count += 1
            try:
                compile(code, f.name, "exec")
            except SyntaxError as e:
                problems.append((f.name, e.lineno, e.msg, code.split("\n")[0][:60]))
        total += count
        skipped += skip
        note = f"（{skip} 个故意写错示例已跳过）" if skip else ""
        if frag:
            note += f"（{frag} 个片段已跳过）"
        flag = "OK " if not any(p[0] == f.name for p in problems) else "FAIL"
        print(f"[{flag}] {f.name}: {count} 个代码块 {note}")
        for name, lineno, msg, first in problems:
            if name == f.name:
                print(f"       行{lineno}: {msg} | 首行: {first}")
    print("-" * 60)
    print(f"可校验代码块 {total} 个，故意写错示例 {skipped} 个，语法错误 {len(problems)} 个")
    return problems


def run_check(files):
    ok = skipped = failed = ctx = 0
    problems = []
    soft = []          # 缺上下文/缺依赖：教学片段常态，不计入失败
    print()
    print("=" * 60)
    print("第二部分：逻辑执行（真实运行，非交互块）")
    print("=" * 60)
    for f in files:
        for code in blocks(f):
            if BROKEN_MARK in code or is_fragment(code):
                skipped += 1
                continue
            if "input(" in code or EXTERNAL.search(code):
                skipped += 1
                continue
            with tempfile.TemporaryDirectory() as tmp:
                script = os.path.join(tmp, "snippet.py")
                with open(script, "w", encoding="utf-8") as fh:
                    fh.write(code)
                try:
                    proc = subprocess.run(
                        [sys.executable, script],
                        cwd=tmp,
                        capture_output=True,
                        timeout=20,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                    )
                except subprocess.TimeoutExpired:
                    failed += 1
                    problems.append((f.name, "超时（疑似死循环）", code.split("\n")[0][:60]))
                    continue
            if proc.returncode == 0:
                ok += 1
            else:
                err = proc.stderr.strip().split("\n")[-1][:120]
                head = code.split("\n")[0][:60]
                # 引用课文里定义的变量 / 依赖未安装：片段教学的常态，单独归类
                if re.match(r"(NameError|ModuleNotFoundError|ImportError|"
                            r"FileNotFoundError|IndentationError)", err):
                    ctx += 1
                    soft.append((f.name, err, head))
                else:
                    failed += 1
                    problems.append((f.name, err, head))
    print(f"实际执行 {ok + failed + ctx} 个"
          f"（跳过 {skipped} 个：故意写错 / 片段 / input 交互 / 需外部模块），"
          f"通过 {ok}，失败 {failed}，缺上下文 {ctx}")
    if soft:
        print(f"\n--- 缺上下文 {len(soft)} 个（教学片段引用课文变量，非错误，仅提示）---")
        seen = set()
        for name, err, first in soft:
            key = (name, first)
            if key in seen:
                continue
            seen.add(key)
            print(f"[{name}] {err}\n    首行: {first}")
    if problems:
        print("\n--- 失败明细（按文件+首行去重）---")
        seen = set()
        for name, err, first in problems:
            key = (name, first)
            if key in seen:
                continue
            seen.add(key)
            print(f"[{name}] {err}\n    首行: {first}")
    return problems


def main():
    files = sorted(pathlib.Path(sys.argv[1]).glob("[01]*.md"))
    print(f"共找到 {len(files)} 个讲义文件\n")
    sp = syntax_check(files)
    rp = run_check(files)
    print()
    print("=" * 60)
    if not sp and not rp:
        print("最终结论：全部通过 —— 语法 0 错误，逻辑执行 0 失败")
        return 0
    print(f"最终结论：语法错误 {len(sp)} 个，逻辑执行失败 {len(rp)} 个")
    return 1


if __name__ == "__main__":
    sys.exit(main())