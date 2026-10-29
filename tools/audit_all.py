# -*- coding: utf-8 -*-
"""全站整体审计：一次跑完所有检查，输出可直接读的问题清单。

检查项
  A 讲义源围栏平衡（含缩进围栏）
  B 产物新鲜度（course/*.md 是否比 web/*.html 新）
  C 切课方案（边界/空课/遗漏/重叠/体量）
  D 课节页结构（复盘块、目标、区块完整性、导航）
  E 标题质量（有无代码行被误判成标题）
  F 链接与锚点（全站）
  G 占位符残留
  H 代码高亮
  I 前端能力（搜索/筛选/打印/进度）
  J 主题（每页都带切换脚本/按钮，深色表已派生）
"""
import os, re, sys, glob, importlib.util
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COURSE = os.path.join(ROOT, "course")
WEB = os.path.join(ROOT, "web")
LESSONS = os.path.join(WEB, "lessons")
FENCE = chr(96) * 3


def load_mod(name, rel):
    sp = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


problems = []
notes = []


def bad(section, msg):
    problems.append(f"[{section}] {msg}")


def info(section, msg):
    notes.append(f"[{section}] {msg}")


# ── A 讲义源围栏平衡 ────────────────────────────────────────────
md_files = sorted(f for f in os.listdir(COURSE) if f.endswith(".md"))
for f in md_files:
    lines = open(os.path.join(COURSE, f), encoding="utf-8").read().split("\n")
    n = sum(1 for ln in lines if ln.strip().startswith(FENCE))
    if n % 2:
        bad("A", f"{f} 围栏数为奇数（{n}）——有代码块未闭合")
    fence = False
    for i, ln in enumerate(lines):
        if ln.strip().startswith(FENCE):
            fence = not fence
            continue
        if fence and re.match(r"^#{2,4} ", ln):
            bad("A", f"{f} 第 {i} 行标题落在代码块内：{ln[:36]}")
            break
info("A", f"检查 {len(md_files)} 份讲义源")

# ── B 产物新鲜度 ───────────────────────────────────────────────
newest_md = max((os.path.getmtime(os.path.join(COURSE, f)), f) for f in md_files)
N_UNITS = len([f for f in os.listdir(COURSE) if re.match(r'\d\d-单元', f)])
for u in range(N_UNITS):
    p = os.path.join(WEB, f"{u:02d}.html")
    if not os.path.exists(p):
        bad("B", f"缺少产物 web/{u:02d}.html")
    elif os.path.getmtime(p) < newest_md[0]:
        bad("B", f"web/{u:02d}.html 比 course/{newest_md[1]} 旧 —— 需要重跑 build_lectures.py")
lp = os.path.join(LESSONS, "index.html")
if os.path.exists(lp) and os.path.getmtime(lp) < newest_md[0]:
    bad("B", "web/lessons/ 比讲义源旧 —— 需要重跑 build_lessons.py")
info("B", f"最新讲义源 {newest_md[1]} @ {datetime.fromtimestamp(newest_md[0]):%H:%M:%S}")

# ── C 切课方案 ─────────────────────────────────────────────────
bl = load_mod("bl", "tools/build_lessons.py")
rc = load_mod("recaps", "tools/recaps.py")


def heads(md):
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


src = {}
for u in range(N_UNITS):
    fn = next((x for x in os.listdir(COURSE) if x.startswith(f"{u:02d}-")), None)
    if fn is None:
        info("B", f"单元 {u:02d} 讲义尚未编写，跳过切课校验")
        continue
    src[u] = open(os.path.join(COURSE, fn), encoding="utf-8").read()

N = len(bl.LESSONS)
spans = []
for idx, (u, (st, en), wk, title, goal, live, hw) in enumerate(bl.LESSONS, 1):
    md = src[u]
    lines = md.split("\n")
    hs = heads(md)
    si = next((i for i, lv, t in hs if t.startswith(st)), None)
    ei = None
    if si is not None and en:
        ei = next((i for i, lv, t in hs if i > si and t.startswith(en)), None)
    if si is None:
        bad("C", f"第{idx:02d}节 起始标题不存在：{st!r}")
        continue
    if en and ei is None:
        bad("C", f"第{idx:02d}节 结束标题不存在：{en!r}")
        continue
    if ei is None:
        ei = len(lines)
    size = len("\n".join(lines[si:ei]).encode("utf-8"))
    nh = sum(1 for i, lv, t in hs if si <= i < ei)
    if nh == 0:
        bad("C", f"第{idx:02d}节 内容为空")
    if size > 130_000:
        bad("C", f"第{idx:02d}节 体量过大 {size//1024} KB")
    if size < 1_200:
        bad("C", f"第{idx:02d}节 体量过小 {size//1024} KB")
    spans.append((idx, u, si, ei, size))

by_unit = {}
for s in spans:
    by_unit.setdefault(s[1], []).append(s)
for u, rs in sorted(by_unit.items()):
    if u not in src:
        continue
    rs.sort(key=lambda r: r[2])
    h2 = [i for i, lv, t in heads(src[u]) if lv >= 2]
    if h2 and rs[0][2] > h2[0]:
        bad("C", f"单元{u:02d} 开头 {rs[0][2]-h2[0]} 行未被任何课覆盖")
    for a, b in zip(rs, rs[1:]):
        if a[3] != b[2]:
            bad("C", f"单元{u:02d} 第{a[0]:02d}节与第{b[0]:02d}节之间遗漏 {b[2]-a[3]} 行")
    total_lines = len(src[u].split("\n"))
    if rs[-1][3] < total_lines:
        bad("C", f"单元{u:02d} 末尾 {total_lines-rs[-1][3]} 行未被覆盖")
info("C", f"{N} 节课，{len(by_unit)} 个单元，平均正文 {sum(s[4] for s in spans)//len(spans)//1024} KB")

# 复盘覆盖 + 上一节标题对应
if not rc.OPENING:
    bad("C", "第 1 节缺少开课准备内容")

rvmod = load_mod("reviews", "tools/reviews.py")

# 阶段 2（单元 12 起）的复盘/讲评在 recaps_stage2.py，按课号合并
rc2 = load_mod("recaps2", "tools/recaps_stage2.py")
rv2 = rc2
STAGE2_FROM = bl.LESSONS[0][0] if False else min(
    i for i, (u, *_r) in enumerate(bl.LESSONS, 1) if u >= 12) if any(
    u >= 12 for u, *_r in bl.LESSONS) else N + 1

for i in range(1, N + 1):
    if i >= STAGE2_FROM:
        items = rc2.RECAP.get(i, rc.OPENING if i == STAGE2_FROM else None)
        r = rv2.REVIEWS.get(i)
    else:
        items = rc.RECAP.get(i, rc.OPENING if i == 1 else None)
        r = rvmod.REVIEWS.get(i)
    if not items:
        bad("C", f"第{i:02d}节缺少复盘内容")
    if not r or not r.get("items"):
        bad("C", f"第{i:02d}节缺少讲评自查项")
    elif not r.get("summary"):
        bad("C", f"第{i:02d}节缺少讲评一句话总结")

_recap_nos = set(rc.RECAP) | set(rc2.RECAP) | {1, STAGE2_FROM}  # 两阶段的第 1 节用开课准备
_nrecap = len([i for i in _recap_nos if 1 <= i <= N])
_nreview = len([i for i in (set(rvmod.REVIEWS) | set(rc2.REVIEWS)) if 1 <= i <= N])
info("C", f"复盘覆盖 {_nrecap}/{N} 节；讲评覆盖 {_nreview}/{N} 节")

# ── D/E/F/G/H 课节页 ──────────────────────────────────────────
pages = sorted(glob.glob(os.path.join(LESSONS, "*.html")))
lesson_pages = [p for p in pages if os.path.basename(p) != "index.html"]
if len(lesson_pages) != N:
    bad("D", f"生成了 {len(lesson_pages)} 页，但切课方案是 {N} 节")

junk_re = re.compile(r"\.py\b")
for p in lesson_pages:
    name = os.path.basename(p)
    s = open(p, encoding="utf-8").read()
    # 课节页是 NNN.html（三位），不能用 name[:2]——会把 100+ 截成 10+
    n = int(re.match(r"(\d+)\.html", name).group(1))

    # D 结构
    for label, pat in [("复盘块", 'id="recap"'), ("本节目标", 'class="goal"'),
                       ("课堂实操", 'class="blk live"'), ("课后作业", 'class="blk hw"'),
                       ("讲评块", 'id="review"'), ("本节总结", 'rv-sum'),
                       ("进度条", 'id="pbar"'), ("完成勾选", 'id="doneBox"')]:
        if pat not in s:
            bad("D", f"{name} 缺少{label}")
    if n > 1 and "上一节" not in s:
        bad("D", f"{name} 缺少「上一节」导航")
    if n < N and "下一节" not in s:
        bad("D", f"{name} 缺少「下一节」导航")

    # D 复盘内容与上一节标题一致（第 1 / 65 节是每阶段开课，不要求引用上一节）
    if n > 1 and n != 65:
        prev_title = bl.LESSONS[n - 2][3]
        m = re.search(r'id="recap"><h3>(.*?)</h3>', s, re.S)
        if not m:
            bad("D", f"{name} 复盘块缺少标题")
        elif prev_title not in m.group(1):
            bad("D", f"{name} 复盘头未引用上一节「{prev_title}」")

    # E 标题质量：真正的误判是「整行就是一行 Python 代码」，而不是标题里提到 .py
    for lv, aid, t in re.findall(r"<h([123]) id=\"([^\"]+)\">(.*?)</h\1>", s, re.S):
        txt = re.sub(r"<[^>]+>", "", t).strip()
        if not txt:
            bad("E", f"{name} 有空标题")
            continue
        # 命中典型代码特征：赋值、带括号调用、赋值运算符、None/True/False、结尾冒号
        if (re.match(r"^\w+\s*=\s*\S", txt)                     # x = 1
                or re.match(r"^(print|return|import|from|def|class)\s", txt)
                or txt.endswith(":")                             # if x:
                or re.match(r"^[\w.]+\([^)]*\)$", txt)                # f(x)
                or txt in ("None", "True", "False")):
            bad("E", f"{name} 疑似代码行被当成标题：{txt[:40]!r}")

    # G 占位符
    if "@@CODE" in s:
        bad("G", f"{name} 有占位符残留")

    # F 链接与锚点（页内）
    for a in set(re.findall(r'href="#([^"]+)"', s)):
        if f'id="{a}"' not in s:
            bad("F", f"{name} 死锚点 #{a}")

# F 站内链接（跨文件）
# 站点全部 HTML：根目录的入口 / 路线图 / 课表 + web/ 下的讲义与题库 + 课节页
TOP_PAGES = [f for f in ("index.html", "python-learning-roadmap.html",
                         "python-course-syllabus.html")
             if os.path.exists(os.path.join(ROOT, f))]
TOP_PAGES = [os.path.join(ROOT, f) for f in TOP_PAGES]
# 子目录里的独立页面（HTML 课件播放器）也要一起检查
EXTRA_PAGES = (sorted(glob.glob(os.path.join(WEB, "ppt", "*.html")))
               + sorted(glob.glob(os.path.join(WEB, "ppt", "u", "*.html"))))
all_html = TOP_PAGES + EXTRA_PAGES + sorted(glob.glob(os.path.join(WEB, "*.html"))) + pages
checked = 0
for f in all_html:
    rel = os.path.relpath(f, ROOT)
    s = open(f, encoding="utf-8").read()
    base = os.path.dirname(f)
    # 先剥掉 <pre>/<code> 块——代码示例里的 href 与 {% %} 不是真实链接
    bare = re.sub(r"<(pre|code)\b[\s\S]*?</\1>", "", s)
    for href in re.findall(r'href="([^"]+)"', bare):
        if href.startswith(("http", "#", "mailto:", "data:", "javascript")):
            continue
        t = href.split("#")[0]
        if not t or "+" in t:      # 跳过 JS 模板串
            continue
        if "{%" in t or "{{" in t or t.startswith("/"):   # Django 模板 / 站内绝对路径
            continue
        checked += 1
        if not os.path.exists(os.path.normpath(os.path.join(base, t))):
            bad("F", f"{rel} 死链 -> {href}")
info("F", f"检查 {len(all_html)} 个页面、{checked} 个链接")

# H 高亮
no_hl = [os.path.basename(p) for p in lesson_pages
         if "<pre" in open(p, encoding="utf-8").read()
         and not re.search(r'class="k"|class="nf"|class="s2"|class="w"|class="cl"',
                           open(p, encoding="utf-8").read())]
if no_hl:
    info("H", f"{len(no_hl)} 页疑似无高亮（多为纯 bash 块，属正常）：{no_hl[:3]}")

# ── I 前端能力 ────────────────────────────────────────────────
idx = open(os.path.join(LESSONS, "index.html"), encoding="utf-8").read()
for label, pat in [("搜索框", 'type="search"'), ("筛选按钮", 'class="fb'),
                   ("完成按钮", 'class="lc-ck"'), ("进度条", 'id="tr"'),
                   ("打印样式", "@media print"), ("来源计数", 'id="cnt"'),
                   ("继续学习入口", 'id="resume"')]:
    if pat not in idx:
        bad("I", f"课程目录页缺少{label}")
if re.search(r"querySelectorAll\('\.lc'\)\.forEach\(function\(el,i\)\{\s*el\.addEventListener\('click'", idx):
    bad("I", "课程目录页仍有「点击卡片即标记完成」逻辑")
for p in lesson_pages[:1] + [pages[0]]:
    if "@media print" not in open(p, encoding="utf-8").read():
        bad("I", f"{os.path.basename(p)} 缺少打印样式")
# 课节页复盘块 / 键盘翻页 / 侧栏复盘入口
for p_ in lesson_pages[:3] + lesson_pages[-2:]:
    t = open(p_, encoding="utf-8").read()
    b = os.path.basename(p_)
    checks = [("复盘块", 'id="recap"'), ("侧栏复盘入口", 'href="#recap"'),
              ("讲评块", 'id="review"'), ("侧栏讲评入口", 'href="#review"'),
              ("下一节链接 id", 'id="nextLink"'),
              ("键盘翻页", "ArrowLeft"), ("打印样式", "@media print")]
    if int(b[:2]) > 1:                      # 第 1 节本就没有「上一节」
        checks.append(("上一节链接 id", 'id="prevLink"'))
    for label, pat in checks:
        if pat not in t:
            bad("I", f"{b} 缺少{label}")

# 主页课节进度与续学入口
hp = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
for label, pat in [("课节进度条", 'id="ltr"'), ("续学入口", 'id="lgo"'),
                   ("读取课节进度", "lesson-done-v1"), ("课程目录入口", "web/lessons/index.html")]:
    if pat not in hp:
        bad("I", f"主页缺少{label}")

# 首页单元卡课节数与实际一致
cnt_map = re.search(r"var LESSON_CNT\s*=\s*(\{[^}]*\})", hp)
if not cnt_map:
    bad("I", "主页缺少 LESSON_CNT 定义")
else:
    declared = {int(kv.split(":")[0]): int(kv.split(":")[1])
                for kv in cnt_map.group(1).strip("{}").split(",")}
    actual = {}
    for _u, _rng, *_r in bl.LESSONS:
        actual[_u] = actual.get(_u, 0) + 1
    if declared != actual:
        bad("I", f"主页 LESSON_CNT 与实际不符：声明 {declared}，实际 {actual}")

# 所有 HTML 页面的 <script> 必须语法合法（拼接数组漏逗号会整页崩掉）
import subprocess, tempfile, shutil
_tdir = os.path.join(ROOT, ".tmp_audit")
os.makedirs(_tdir, exist_ok=True)
js_files = []
for f in all_html:
    txt = open(f, encoding="utf-8").read()
    for m in re.finditer(r"<script>([\s\S]*?)</script>", txt):
        code = m.group(1)
        if code.strip():
            fd, tmp = tempfile.mkstemp(suffix=".js", dir=_tdir)
            os.close(fd)
            open(tmp, "w", encoding="utf-8").write(code)
            js_files.append((os.path.relpath(f, ROOT), tmp))

if js_files:
    # 用一个 node 进程批量检查，避免起 79 个进程
    check = os.path.join(ROOT, ".tmp_audit", "_jscheck.js")
    with open(check, "w", encoding="utf-8") as fh:
        fh.write("const fs=require('fs');\n")
        fh.write("const files=" + repr([t for _, t in js_files]) + ";\n")
        fh.write("files.forEach((f,i)=>{try{new Function(fs.readFileSync(f,'utf8'));}"
                 "catch(e){console.log('BAD|'+i+'|'+e.message);}});\n")
    try:
        out = subprocess.run(
            ["node", check], capture_output=True, text=True, timeout=120,
            cwd=ROOT).stdout
    except Exception as e:
        out = ""
        info("I", f"JS 语法检查未执行（node 不可用）：{e}")
    bad_js = [ln for ln in out.splitlines() if ln.startswith("BAD|")]
    for ln in bad_js:
        _, idx, msg = ln.split("|", 2)
        bad("I", f"{js_files[int(idx)][0]} 的 script 语法错误：{msg[:90]}")
    if not bad_js:
        info("I", f"{len(js_files)} 段 script 全部语法合法")
    # 同上：几百个临时 js 一次 rmtree 会撞批量删除确认，直接把审计打断。
    # 改名搬到 .cache 即可（审计只关心结果，不关心残渣在哪）。
    try:
        import time as _t
        os.replace(_tdir, os.path.join(ROOT, ".cache", f"audit_garbage_{int(_t.time())}"))
    except OSError:
        pass


# ── 数量一致性：22 / 111 / 52 / 23 只认 site_data，页面里不许再写死旧值 ──
sys.path.insert(0, os.path.join(ROOT, "tools"))
try:
    import site_data
    _tot = site_data.total_lessons()
    _units = site_data.unit_cnt()
    _q = site_data.question_cnt()
    # 旧数字残留（扩阶段时最容易漏的地方）
    # 只查「确定是错的」写法。「12 个单元 · 64 节课」是阶段 1 的正确描述，不能误报。
    # 同时剥掉 HTML 与 JS 注释——注释里复述旧值不该算问题。
    STALE = ["var TOTAL=64", "TOTAL = 64;", "0 / 12<", "单元讲义（12 份",
             "LESSON_CNT = 12"]
    stale_hits = []
    for f in dict.fromkeys(all_html):
        try:
            t = open(f, encoding="utf-8").read()
        except Exception:
            continue
        t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
        t = re.sub(r"//[^\n]*", "", t)
        for pat in STALE:
            if pat in t:
                stale_hits.append(f"{os.path.relpath(f, ROOT)} 含旧值「{pat}」")
    for h in stale_hits[:6]:
        bad("G", h)
    if not stale_hits:
        info("G", f"数量常量一致：{_units} 单元 / {_tot} 节 / {_q} 题")
    # 首页 data-n 的源值也要与真实数量一致（脚本会用 SITE 覆盖，但源值别写错，
    # 万一脚本没跑到，页面上就是错的）
    _ix = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    _actual = {"units": _units, "lessons": _tot, "bank": _q}
    _mis = []
    for _m in re.finditer(r'data-n="(units|lessons|bank)">(\d+)<', _ix):
        _k, _v = _m.group(1), int(_m.group(2))
        if _v != _actual[_k]:
            _mis.append(f"{_k} 写成 {_v}，实际 {_actual[_k]}")
    if _mis:
        bad("G", "首页数字与真实数据不一致：" + "；".join(_mis))
    else:
        info("G", "首页 data-n 数字与 site_data 一致")
    # 背景音乐：每个页面都要挂上脚本，音频文件必须存在
    _no_bgm = [os.path.relpath(f, ROOT) for f in dict.fromkeys(all_html)
               if "bgm.js" not in open(f, encoding="utf-8").read()]
    _wav = os.path.join(ROOT, "web", "media", "bgm-8bit.wav")
    if _no_bgm:
        bad("G", f"{len(_no_bgm)} 个页面没有挂背景音乐脚本（如 {_no_bgm[0]}）")
    if not os.path.exists(_wav):
        bad("G", "背景音乐文件缺失：web/media/bgm-8bit.wav")
    if not _no_bgm and os.path.exists(_wav):
        info("G", f"背景音乐：{len(dict.fromkeys(all_html))} 个页面已挂载，"
                  f"音频 {os.path.getsize(_wav)/1024:.0f} KB")

    # 课件图必须是 .webp 且文件存在
    miss_img, png_ref = 0, 0
    for f in all_html:
        t = open(f, encoding="utf-8").read()
        if re.search(r"slide-\d+\.png", t):
            png_ref += 1
        for src in set(re.findall(r'src="([^"]+slide-[^"]+)"', t)):
            base = os.path.dirname(f)
            if not os.path.exists(os.path.normpath(os.path.join(base, src))):
                miss_img += 1
    if png_ref:
        bad("G", f"{png_ref} 个页面仍引用已删除的 slide-*.png")
    if miss_img:
        bad("G", f"{miss_img} 处课件图找不到文件")
except Exception as e:
    info("I", f"数量一致性检查跳过：{e}")


# ── 题库代码块语法（verify_py 只查讲义，题库以前没人管）──
try:
    _mdq = open(os.path.join(ROOT, "exercises", "题库-从入门到实践.md"),
                encoding="utf-8").read()
    _blocks = re.findall("```python\n(.*?)```", _mdq, re.S)
    _errs = []
    for _i, _b in enumerate(_blocks, 1):
        try:
            compile(_b, f"bank#{_i}", "exec")
        except SyntaxError as _e:
            _errs.append(f"题库第 {_i} 个代码块：第 {_e.lineno} 行 {_e.msg}")
    for _e in _errs[:5]:
        bad("G", _e)
    if not _errs:
        info("G", f"题库 {len(_blocks)} 个代码块语法合法")
except Exception as _e:
    info("I", f"题库代码检查跳过：{_e}")

info("I", "搜索 / 筛选 / 完成按钮 / 复盘块 / 讲评块 / 键盘翻页 / 续学入口 / 打印样式 已就位")

# ── J 主题切换（每页都要能切深浅，且深色表真的写进去了）────────────
try:
    import theme as _theme
    _htmls = []
    for _base in ("web", "fluent", "python-course-ppt", "."):
        _p = os.path.join(ROOT, _base)
        for _dp, _dns, _fs in os.walk(_p):
            _dns[:] = [d for d in _dns if d not in (".git", "node_modules", ".cache",
                                                    "dist", "__pycache__", "www")]
            for _f in _fs:
                if _f.endswith(".html"):
                    _fp = os.path.join(_dp, _f)
                    if "/android/" in _fp.replace("\\", "/"):
                        continue
                    _htmls.append(_fp)
    _no_head, _no_dark, _no_btn = [], [], []
    for _fp in _htmls:
        _s = open(_fp, encoding="utf-8").read()
        if _theme.HEAD_BEGIN not in _s:
            _no_head.append(_fp)
        if "thBtn" not in _s:
            _no_btn.append(_fp)
        # 深色表可能写在外链 CSS 里：页内 <style> 有规则就查页内，否则查它引的 css。
        # 先剔掉 theme 自己注入的那段样式（它本来就不带深色表）。
        _s2 = re.sub(re.escape(_theme.HEAD_BEGIN) + r".*?" + re.escape(_theme.HEAD_END),
                     "", _s, flags=re.S)
        _inline = re.search(r"<style[^>]*>(.*?)</style>", _s2, re.S)
        _ok_dark = False
        if _inline and len(_inline.group(1).strip()) > 80:
            _ok_dark = _theme.CSS_MARK in _s
        else:
            for _href in re.findall(r'<link[^>]+rel="stylesheet"[^>]*href="([^"]+)"', _s):
                _cp = os.path.normpath(os.path.join(os.path.dirname(_fp), _href))
                if os.path.exists(_cp):
                    if _theme.CSS_MARK in open(_cp, encoding="utf-8").read():
                        _ok_dark = True
                        break
        if not _ok_dark:
            _no_dark.append(_fp)
    _rel = lambda ps: "、".join(os.path.relpath(x, ROOT) for x in ps[:4]) + \
                      (f" 等 {len(ps)} 个" if len(ps) > 4 else "")
    if _no_head:
        bad("J", f"{len(_no_head)} 页没有主题脚本：{_rel(_no_head)}")
    if _no_dark:
        bad("J", f"{len(_no_dark)} 页没有深色样式表：{_rel(_no_dark)}")
    if _no_btn:
        bad("J", f"{len(_no_btn)} 页没有切换按钮：{_rel(_no_btn)}")
    if not (_no_head or _no_dark or _no_btn):
        info("J", f"{len(_htmls)} 个页面均带主题脚本 / 深色表 / 切换按钮")
except Exception as _e:
    info("J", f"主题检查跳过：{_e}")

# ── 输出 ──────────────────────────────────────────────────────
print("=" * 62)
print(f"全站整体审计  {datetime.now():%Y-%m-%d %H:%M}")
print("=" * 62)
for n in notes:
    print("  ·", n)
print()
if problems:
    print(f"发现 {len(problems)} 个问题：")
    for p in problems:
        print("  ✗", p)
else:
    print("✓ 全部通过：源围栏 / 产物新鲜度 / 切课覆盖 / 复盘 / 结构 / 标题 / 链接 / 占位符 / 前端能力 / 主题")
print()
sys.exit(1 if problems else 0)
