"""校验「运行结果」块是否与真实输出一致。

为什么需要：`verify_course.py` 只检查代码块能不能跑（rc == 0），
但页面上还写着一段「运行结果」。代码改了、输出块没跟着改，读者照样被误导——
而且这种错 rc 永远是 0，现有工具链一个都抓不到。

配对规则（保守，避免误报）：
   ```python ... ```
   （空行 / 「运行结果：」「输出：」这一行）
   ```text ... ```
只有紧跟「运行结果/输出」提示语的 text 块才当作程序输出比对；
讲义里那些用来展示 JSON 结构、数据结构示意 的 text 块不参与。

跳过：`# （片段）`、含 input()、依赖未安装库的块、输出里含 …/.../（略） 的块。

用法：
  python tools/check_outputs.py            # 全量，只报告
  python tools/check_outputs.py 17 21      # 只看指定单元
  python tools/check_outputs.py --show     # 打印每个不一致的前后对照
"""

import re
import subprocess
import sys
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
COURSE = ROOT / "course"

# 输出与提示语之间允许的间隔行数（空行、「run 一下」这类过渡句）
GAP = 3
HINT = re.compile(r"^(运行结果|输出|执行结果|实际输出)[：:]?\s*$")

# 本机没装的库：这些块无法实跑，直接跳过（与 verify_course 的判定保持一致）
MISSING_LIBS = ("pygame", "matplotlib", "plotly", "requests", "django", "pandas", "pytest")
TRUNC = ("…", "...", "（略）", "省略")


def blocks(text):
    """返回 [(kind, start_line, content)]，kind 取 'python' / 'text'。"""
    out, lines = [], text.split("\n")
    i = 0
    while i < len(lines):
        m = re.match(r"^```(\w*)\s*$", lines[i])
        if not m:
            i += 1
            continue
        lang = m.group(1)
        j = i + 1
        buf = []
        while j < len(lines) and not lines[j].startswith("```"):
            buf.append(lines[j])
            j += 1
        out.append((lang, i, "\n".join(buf), j))   # j = 关闭围栏所在行
        i = j + 1
    return out


def pairs(bs):
    """python 块 → 其后（间隔 ≤GAP 行、含提示语）的 text 块。"""
    for a, b in zip(bs, bs[1:]):
        if a[0] != "python" or b[0] != "text":
            continue
        gap = b[1] - (a[3] + 1)      # a[3] 是 python 块关闭围栏的行号
        if gap > GAP:
            continue
        between = _LINES[a[3] + 1:b[1]]
        if not any(HINT.match(ln.strip()) for ln in between):
            continue
        yield a, b


def runnable(code):
    head = code.split("\n")[0]
    if "（片段）" in head:
        return False, "片段"
    if "input(" in code:
        return False, "含 input"
    for lib in MISSING_LIBS:
        if re.search(r"^\s*(?:import|from)\s+" + lib + r"\b", code, re.M):
            return False, f"缺 {lib}"
    return True, ""


def main(argv):
    only = {int(x) for x in argv if x.isdigit()}
    show = "--show" in argv
    files = sorted(COURSE.glob("*.md"))
    total = checked = 0
    bad = []
    global _LINES
    for f in files:
        no = int(f.name[:2])
        if only and no not in only:
            continue
        _LINES = f.read_text(encoding="utf-8").split("\n")
        bs = blocks("\n".join(_LINES))
        for code_blk, out_blk in pairs(bs):
            total += 1
            code = code_blk[2]
            expect = out_blk[2].strip()
            if not expect or any(t in expect for t in TRUNC):
                continue
            ok, why = runnable(code)
            if not ok:
                continue
            try:
                p = subprocess.run([sys.executable, "-c", code],
                                   capture_output=True, text=True, encoding="utf-8",
                                   timeout=30)
            except subprocess.TimeoutExpired:
                bad.append((f.name, code_blk[1] + 1, "超时", "", ""))
                continue
            checked += 1
            got = p.stdout.strip()
            if p.returncode != 0:
                bad.append((f.name, code_blk[1] + 1, "运行失败",
                            p.stderr.strip().split("\n")[-1], expect))
                continue
            if got != expect:
                bad.append((f.name, code_blk[1] + 1, "输出不一致", got, expect))

    print(f"「运行结果」块 {total} 个，可实跑比对 {checked} 个，不一致 {len(bad)} 个")
    for name, line, kind, got, expect in bad:
        print(f"\n[{name}:{line}] {kind}")
        if show and got:
            print("  实跑：" + got.replace("\n", " ⏎ ")[:300])
            print("  页面：" + expect.replace("\n", " ⏎ ")[:300])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
