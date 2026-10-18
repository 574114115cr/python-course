"""把讲义中成对的「被测模块 + 测试模块」代码块写进临时目录，用 pytest 真跑一遍。

配对规则：测试文件 test_xxx.py 只与【同一个 md 文件里】出现在它之前的最近的 xxx.py 配对。
如果测试文件 import 的模块名与该被测模块一致，才算有效配对。
"""
import re
import pathlib
import sys
import os
import re as _re
import tempfile
import subprocess

CODE_RE = _re.compile(r"```python\n(.*?)```", _re.DOTALL)
BROKEN = "INTENTIONALLY-BROKEN"


def parse(path):
    """返回 [(filename_hint, code)]。"""
    out = []
    for code in CODE_RE.findall(path.read_text(encoding="utf-8")):
        first = code.split("\n")[0]
        m = _re.match(r"^\s*#\s*([\w\-.]+\.py)\s*——", first)
        if m and BROKEN not in first:
            out.append((m.group(1), code))
    return out


def main():
    files = sorted(pathlib.Path(sys.argv[1]).glob("[01]*.md"))
    results = {"pass": 0, "fail": 0, "skip": 0, "orphan": 0}
    problems = []

    for f in files:
        items = parse(f)
        # 记录每个"被测模块名 -> 最近的代码"
        mod_codes = {}
        order = []
        for name, code in items:
            base = name[:-3]
            if not base.startswith("test_"):
                mod_codes[base] = code
                order.append(base)

        for name, code in items:
            base = name[:-3]
            if not base.startswith("test_"):
                continue
            # 找出这个测试文件 import 了哪个本地模块
            imported = [
                m for m in _re.findall(r"^from\s+([\w]+)\s+import|^import\s+([\w]+)", code, _re.M)
                for m in m if m in mod_codes
            ]
            if not imported:
                results["orphan"] += 1
                problems.append((f.name, name, "找不到对应的被测模块（可能需手动配对）"))
                continue

            mod = imported[0]
            if "input(" in mod_codes[mod]:
                results["skip"] += 1
                continue

            # 需要额外依赖的情况跳过
            if _re.search(r"^import\s+(requests)\b", mod_codes[mod], _re.M):
                results["skip"] += 1
                continue

            with tempfile.TemporaryDirectory() as tmp:
                for fname, fcode in [(mod + ".py", mod_codes[mod]),
                                     (name, code)]:
                    with open(os.path.join(tmp, fname), "w", encoding="utf-8") as fh:
                        fh.write(fcode)
                try:
                    proc = subprocess.run(
                        [sys.executable, "-m", "pytest", "-q", "--no-header",
                         "-p", "no:cacheprovider"],
                        cwd=tmp, capture_output=True, text=True,
                        encoding="utf-8", errors="replace", timeout=120,
                    )
                except subprocess.TimeoutExpired:
                    results["fail"] += 1
                    problems.append((f.name, f"{mod}.py + {name}", "超时"))
                    continue

            if proc.returncode == 0:
                results["pass"] += 1
            else:
                # buggy.py 的测试本来就该失败（练习 10-4 的教学目的）
                if mod in ("buggy",):
                    results["skip"] += 1
                    continue
                results["fail"] += 1
                tail = [l for l in proc.stdout.strip().split("\n") if l.strip()]
                summary = next((l for l in reversed(tail) if "passed" in l or "failed" in l
                                or "error" in l), tail[-1] if tail else "")[:140]
                problems.append((f.name, f"{mod}.py + {name}", summary))

    print("=" * 62)
    print(f"pytest 实跑结果：")
    print(f"  通过 {results['pass']}，失败 {results['fail']}，"
          f"跳过 {results['skip']}（故意失败/需交互/需外部依赖），"
          f"未配对 {results['orphan']}")
    print("=" * 62)
    for md, pair, err in problems:
        print(f"[{md}] {pair}\n    {err}")
    return 1 if results["fail"] or results["orphan"] else 0


if __name__ == "__main__":
    sys.exit(main())