"""案例自检：结构、行数、语法，可选实跑。

用法：
    python tools/check_cases.py            # 只编译不执行
    python tools/check_cases.py --run      # 实跑 24 个代码块，并校验两次输出一致
"""
import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASES = os.path.join(ROOT, "course-fluent", "cases")
PY = sys.executable


def eff_lines(code):
    return sum(1 for l in code.splitlines()
               if l.strip() and not l.strip().startswith("#"))


def load():
    out = []
    for fn in sorted(os.listdir(CASES)):
        m = re.match(r"^u(\d\d)\.md$", fn)
        if not m:
            continue
        path = os.path.join(CASES, fn)
        md = open(path, encoding="utf-8").read()
        h1 = re.search(r"(?m)^#\s+单元\s*\d+\s*综合案例\s*[·:：]\s*(.+)$", md)
        blocks = re.findall(r"```python\n(.*?)```", md, re.S)
        out.append({"no": int(m.group(1)), "file": fn, "title": h1.group(1) if h1 else "",
                    "blocks": blocks, "md": md})
    return out


def run_block(code, timeout):
    proc = subprocess.run([PY, "-c", code], capture_output=True, text=True,
                          timeout=timeout, encoding="utf-8", errors="replace")
    return proc.returncode, proc.stdout, proc.stderr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--timeout", type=int, default=30)
    args = ap.parse_args()

    cases = load()
    fails = []
    if [c["no"] for c in cases] != list(range(1, 13)):
        fails.append(f"案例编号不连续：{[c['no'] for c in cases]}")

    for c in cases:
        n = c["no"]
        if not c["title"]:
            fails.append(f"u{n:02d} 缺少标题")
        if len(c["blocks"]) != 2:
            fails.append(f"u{n:02d} 代码块应为 2 个，实际 {len(c['blocks'])}")
            continue
        if "### 重构前" not in c["md"] or "### 重构后" not in c["md"]:
            fails.append(f"u{n:02d} 缺少「重构前/重构后」小节")
        if "### 差异说明" not in c["md"]:
            fails.append(f"u{n:02d} 缺少差异说明")
        rows = len(re.findall(r"(?m)^\|.*\|\s*$", c["md"].split("### 差异说明", 1)[-1]))
        if rows < 6:                     # 表头 + 分隔 + 至少 4 行
            fails.append(f"u{n:02d} 差异表不足 5 行（{rows - 2}）")

        lines = []
        for i, code in enumerate(c["blocks"], 1):
            try:
                compile(code, f"<u{n:02d}#{i}>", "exec")
            except SyntaxError as e:
                fails.append(f"u{n:02d} 第 {i} 块语法错误：{e}")
                continue
            lines.append(eff_lines(code))

        if len(lines) == 2:
            a, b = lines
            if a < 15 or b < 25 or a + b < 40:
                fails.append(f"u{n:02d} 太薄：{a} / {b} 行")
            if b < a * 0.9:
                fails.append(f"u{n:02d} 重构后（{b}）比重构前（{a}）缩水太多")

        if args.run and len(c["blocks"]) == 2:
            # 计时类输出（小数）在两次运行之间本来就不同，比较前先把小数抹成 N；
            # 整数（成功/失败计数等）仍然逐一比对。
            def norm(s):
                return re.sub(r"\d+\.\d+", "N", s)

            outs = []
            for i, code in enumerate(c["blocks"], 1):
                try:
                    rc1, out1, err1 = run_block(code, args.timeout)
                    rc2, out2, _ = run_block(code, args.timeout)
                except subprocess.TimeoutExpired:
                    fails.append(f"u{n:02d} 第 {i} 块超时（>{args.timeout}s）")
                    continue
                if rc1 != 0:
                    fails.append(f"u{n:02d} 第 {i} 块运行失败：{err1.strip().splitlines()[-1:]}")
                if norm(out1) != norm(out2):
                    fails.append(f"u{n:02d} 第 {i} 块两次输出不一致")
                if not out1.strip():
                    fails.append(f"u{n:02d} 第 {i} 块没有输出")
                outs.append(out1)

    print(f"案例 {len(cases)} 个，代码块 {sum(len(c['blocks']) for c in cases)} 个")
    if fails:
        print(f"✗ {len(fails)} 个问题：")
        for f in fails:
            print("   -", f)
        sys.exit(1)
    print("✓ 全部通过" + ("（含实跑）" if args.run else ""))


if __name__ == "__main__":
    main()
