"""源码走读自检：跑每篇的 python 块，把真实输出写回「## 运行输出」。

用法：
    python tools/check_walk.py          # 只跑，不改文件
    python tools/check_walk.py --write  # 跑完把输出写回 md
"""
import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WALK = os.path.join(ROOT, "course-fluent", "walk")
PY = sys.executable

HEAD = re.compile(r"^@@u(\d{2})\|(.+)$", re.M)
CODE = re.compile(r"```python\n(.*?)```", re.S)
OUTBOX = re.compile(r"(## 运行输出\s*\n+```text\n)(.*?)(\n```)", re.S)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--timeout", type=int, default=40)
    args = ap.parse_args()

    files = sorted(f for f in os.listdir(WALK) if re.fullmatch(r"u\d{2}\.md", f))
    if len(files) != 12:
        print(f"!! 走读篇数应为 12，实际 {len(files)}")
    bad = []
    for fn in files:
        path = os.path.join(WALK, fn)
        md = open(path, encoding="utf-8").read()
        h = HEAD.search(md)
        code = CODE.search(md)
        box = OUTBOX.search(md)
        if not h:
            bad.append((fn, "首行缺少「@@uNN|标题」"))
            continue
        if not code:
            bad.append((fn, "缺少 python 代码块"))
            continue
        if not box:
            bad.append((fn, "缺少「## 运行输出 + ```text」占位"))
            continue
        try:
            proc = subprocess.run([PY, "-c", code.group(1)], capture_output=True,
                                  text=True, timeout=args.timeout,
                                  encoding="utf-8", errors="replace")
        except subprocess.TimeoutExpired:
            bad.append((fn, f"超时（>{args.timeout}s）"))
            continue
        if proc.returncode != 0:
            last = proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else "?"
            bad.append((fn, f"运行失败：{last}"))
            continue
        out = proc.stdout.rstrip("\n")
        if not out.strip():
            bad.append((fn, "没有输出"))
            continue
        lines = out.splitlines()
        print(f"[OK ] {fn} {h.group(2)[:38]} → {len(lines)} 行输出")
        if args.write:
            new = md[:box.start(2)] + out + md[box.end(2):]
            if new != md:
                open(path, "w", encoding="utf-8").write(new)
                print("       ↳ 已写回真实输出")

    print()
    if bad:
        print(f"✗ {len(bad)} 个问题：")
        for fn, why in bad:
            print(f"   - {fn}: {why}")
        return 1
    print(f"✓ {len(files)} 篇走读全部实跑通过" + ("（输出已写回）" if args.write else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
