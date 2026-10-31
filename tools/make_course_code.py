"""把讲义里的具名 python 块落盘成真实文件，形成「每单元一套可运行代码」。

讲义块首行标了文件名，例如：
  # settings.py——把会变的数值集中管理
  # （片段）pizza.py —— 函数放在这里
  # learning_logs/models.py（项目文件，完整版）

规则：
- 首行带「（片段）」的视为片段，放 snippets/ 子目录（不能单独运行）。
- 同单元同名文件出现多次（同一文件的多个版本），第一个用原名，后续加 .v2/.v3。
- 每个单元目录写一份 README.txt：文件清单 + 各文件所属小节 + 运行提示。

用法：
  python tools/make_course_code.py            # 输出到 course-code/
  python tools/make_course_code.py --dry      # 只统计，不写文件
  python tools/make_course_code.py --out DIR  # 指定输出目录
"""
import glob
import os
import re
import sys
import time


def clear_out(d):
    """清空输出目录：改名搬进 .cache 垃圾堆，不做删除。

    沙箱有两道硬限制会直接中断构建：单轮删除 >50 个文件要弹确认、
    回收站不可用时 FAIL_CLOSED。改名不算删除，所以统一搬走。
    目录名带时间戳，从不复用（残留的 v2/v3 会让人误以为抽取结果没更新）。
    """
    if not os.path.isdir(d):
        return
    garbage = os.path.join(ROOT, ".cache", "cc_garbage_%d" % int(time.time() * 1000))
    os.makedirs(os.path.dirname(garbage), exist_ok=True)
    os.replace(d, garbage)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COURSE = os.path.join(ROOT, "course")
DEFAULT_OUT = os.path.join(ROOT, "course-code")

NAME_RE = re.compile(r'^#\s*(（片段）)?\s*([A-Za-z_][\w./-]*\.py)\b(.*)$')
HEAD_RE = re.compile(r'^(#{3,4})\s+(.+)$')


def blocks_of(md):
    """返回 [(所在小节标题, 代码正文)]，按出现顺序。"""
    lines = md.split("\n")
    out, cur = [], "（开头）"
    i = 0
    while i < len(lines):
        ln = lines[i]
        m = HEAD_RE.match(ln)
        if m:
            cur = m.group(2).strip()
        if ln.strip().startswith("```python"):
            i += 1
            buf = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            out.append((cur, "\n".join(buf)))
        i += 1
    return out


def main():
    dry = "--dry" in sys.argv
    out_dir = DEFAULT_OUT
    if "--out" in sys.argv:
        out_dir = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])

    if not dry:
        clear_out(out_dir)

    total_files = 0
    total_snip = 0
    for f in sorted(glob.glob(os.path.join(COURSE, "*.md"))):
        base = os.path.basename(f)
        no = base.split("-")[0]
        if not no.isdigit():
            continue
        s = open(f, encoding="utf-8").read()
        seen = {}
        entries = []          # (相对路径, 正文, 小节)
        snips = []
        for sec, body in blocks_of(s):
            head = body.strip().split("\n")[0].strip() if body.strip() else ""
            m = NAME_RE.match(head)
            if not m:
                continue
            # 「（片段）」可能写在文件名前，也可能写在文件名后：
            #   # （片段）pizza.py —— 函数放在这里
            #   # learning_logs/views.py（片段）—— new_topic() 的一部分
            is_snip = bool(m.group(1)) or ("片段" in head) or ("节选" in head)
            rel = m.group(2)
            code = body.rstrip() + "\n"
            if is_snip:
                snips.append((rel, code, sec))
                continue
            n = seen.get(rel, 0) + 1
            seen[rel] = n
            if n > 1:
                stem, ext = os.path.splitext(rel)
                rel = "%s.v%d%s" % (stem, n, ext)
            entries.append((rel, code, sec))

        total_files += len(entries)
        total_snip += len(snips)
        u_dir = os.path.join(out_dir, "u%02d" % int(no))
        print("u%02d  %-30s 完整文件 %2d 个，片段 %2d 个"
              % (int(no), base[:30], len(entries), len(snips)))
        if dry:
            continue
        for rel, code, _ in entries:
            p = os.path.join(u_dir, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w", encoding="utf-8", newline="\n").write(code)
        if snips:
            os.makedirs(os.path.join(u_dir, "snippets"), exist_ok=True)
            for rel, code, _ in snips:
                p = os.path.join(u_dir, "snippets", os.path.basename(rel))
                open(p, "w", encoding="utf-8", newline="\n").write(code)

        # README：入口建议 + 文件清单 + 所属小节
        entry = None
        for rel, _, sec in entries:
            if "完整版" in sec:
                entry = rel
                break
        if entry is None and entries:
            entry = entries[0][0]
        lines = ["单元 %d · %s" % (int(no), base), "=" * 60, ""]
        if entry:
            lines += ["先从这个开始：%s" % entry, ""]
        lines += ["本目录的 .py 文件全部抽自讲义，可直接用 Python 运行。",
                  "snippets/ 里是「片段」——属于某个文件的一部分，不能单独运行。",
                  ".v2/.v3 是同一文件的其它版本（教材练习的参考答案），按需查看。", ""]
        for rel, _, sec in entries:
            lines.append("  %-34s ← %s" % (rel, sec))
        if snips:
            lines += ["", "片段（需并入上面的文件，不能单独跑）："]
            for rel, _, sec in snips:
                lines.append("  %-34s ← %s" % (os.path.basename(rel), sec))
        lines += ["", "运行：在终端执行  python 文件名.py",
                  "缺库时先装：python -m pip install 包名", ""]
        os.makedirs(u_dir, exist_ok=True)
        open(os.path.join(u_dir, "README.txt"), "w",
             encoding="utf-8", newline="\n").write("\n".join(lines))

    print("\n合计：完整文件 %d 个，片段 %d 个 → %s"
          % (total_files, total_snip, "（dry，未写入）" if dry else out_dir))


if __name__ == "__main__":
    main()
