"""校验切课方案：① 边界存在 ② 无空课 ③ 无遗漏 ④ 无重叠 ⑤ 体量均衡。"""
import os, re, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_s = importlib.util.spec_from_file_location("bl", os.path.join(ROOT, "tools", "build_lessons.py"))
m = importlib.util.module_from_spec(_s)
_s.loader.exec_module(m)

FENCE = chr(96) * 3


def load(u):
    f = next((x for x in os.listdir(m.COURSE) if x.startswith(f"{u:02d}-")), None)
    if f is None:
        raise FileNotFoundError(f"单元 {u:02d} 讲义尚未编写")
    return f, open(os.path.join(m.COURSE, f), encoding="utf-8").read()


def headings(md):
    """返回 [(行号, 级别, 标题)]，围栏外。"""
    out, fence = [], False
    for i, ln in enumerate(md.split("\n")):
        if ln.strip().startswith(FENCE):
            fence = not fence
            continue
        if fence:
            continue
        g = re.match(r"^(#{1,4}) (.+)$", ln)
        if g:
            out.append((i, len(g.group(1)), g.group(2).strip()))
    return out


cache = {}
problems = []
rows = []

for idx, (u, (st, en), wk, title, goal, live, hw) in enumerate(m.LESSONS, 1):
    if u not in cache:
        cache[u] = load(u)
    fname, md = cache[u]
    lines = md.split("\n")
    hs = headings(md)

    si = next((i for i, lv, t in hs if t.startswith(st)), None)
    ei = None
    if si is not None and en:
        ei = next((i for i, lv, t in hs if i > si and t.startswith(en)), None)

    if si is None:
        problems.append(f"第{idx:02d}节 起始标题未找到：{st!r}（{fname}）")
        continue
    if en and ei is None:
        problems.append(f"第{idx:02d}节 结束标题未找到：{en!r}（{fname}）")
        continue
    if ei is None:
        ei = len(lines)
    size = len("\n".join(lines[si:ei]).encode("utf-8"))
    nh = sum(1 for i, lv, t in hs if si <= i < ei)
    if nh == 0:
        problems.append(f"第{idx:02d}节 内容为空")
    if size > 130_000:
        problems.append(f"第{idx:02d}节 体量过大：{size//1024} KB（建议一节课 ≤127 KB）")
    if size < 1_200:
        problems.append(f"第{idx:02d}节 体量过小：{size//1024} KB（疑似只切到一个空小节）")
    rows.append((idx, u, wk, title, si, ei, size, nh, fname))

# 覆盖度：每个单元的讲义是否被连续覆盖
by_unit = {}
for r in rows:
    by_unit.setdefault(r[1], []).append(r)
for u, rs in by_unit.items():
    rs.sort(key=lambda r: r[4])
    fname = rs[0][8]
    md = load(u)[1]
    lines = md.split("\n")
    hs = headings(md)
    # 以第一个二级标题为基准；H1 标题块由课程页头部呈现，不重复计入
    h2 = [i for i, lv, t in hs if lv >= 2]
    first = h2[0] if h2 else 0
    if rs[0][4] > first:
        problems.append(f"单元{u:02d} 开头 {rs[0][4]-first} 行未被覆盖（{fname}）")
    for a, b in zip(rs, rs[1:]):
        if a[5] != b[4]:
            problems.append(f"单元{u:02d} 第{a[0]:02d}节与第{b[0]:02d}节之间遗漏 {b[4]-a[5]} 行")
    if rs[-1][5] < len(lines):
        problems.append(f"单元{u:02d} 末尾 {len(lines)-rs[-1][5]} 行未被覆盖（{fname}）")

print(f"共 {len(m.LESSONS)} 节课\n")
print(f"{'节':>4} {'单元':>4} {'周次':>6} {'KB':>5} {'标题':>4}  课程标题")
for idx, u, wk, title, si, ei, size, nh, _f in rows:
    mark = " <<<" if size > 90_000 else ""
    print(f"{idx:>4} {u:>4} {wk:>6} {size//1024:>5} {nh:>4}  {title}{mark}")

if problems:
    print(f"\n发现 {len(problems)} 个问题：")
    for p in problems:
        print("  -", p)
else:
    print("\n全部通过：无空课、无遗漏、无重叠、体量均衡。")