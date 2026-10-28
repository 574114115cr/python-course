# -*- coding: utf-8 -*-
"""从讲义生成「逐节版」讲授课件：每单元一份 deck，每节课 2 页实质内容。

结构（每单元）：
  封面 → 每节课〔课节页 + 知识点页〕 → 单元小结
内容来源：
  - 课节页：tools/build_lessons.py 的 LESSONS（目标 / 实操 / 作业）
  - 知识点页：该节课对应的讲义切片里的 h3 标题 + 要点
产物：
  - DSL：python-course-ppt/lessons-deck/NN/NN.slide
  - PPTX：由调用方用 slidep 构建
"""
import importlib.util
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
COURSE = os.path.join(ROOT, "course")

# 与课件统一的设计语言
BG = "#FAFCFE"
P1 = "#1F5FA8"      # 主色
P2 = "#0E9B78"      # 辅色
P3 = "#E08A15"      # 强调
INK = "#16232E"
MUTED = "#5A6B7A"
LINE = "#D8E3EE"
CJK = "Microsoft YaHei"


def load(name, rel):
    sp = importlib.util.spec_from_file_location(name, os.path.join(TOOLS, rel))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


bl = load("bl", "build_lessons.py")
pm = load("pm", "ppt_map.py")

TOTAL_LESSONS = len(bl.LESSONS)


# ── 文本清洗：DSL 是 JSX 风格，正文里出现 < > { } 会被当成语法 ──
def esc(t, limit=None):
    t = re.sub(r"`+", "", str(t))
    t = re.sub(r"\*+", "", t)
    t = re.sub(r"\$+", "", t)
    t = t.replace("<", "＜").replace(">", "＞")
    t = t.replace("{", "｛").replace("}", "｝")
    t = t.replace("&", "＆")
    t = re.sub(r"\s+", " ", t).strip()
    if limit and len(t) > limit:
        cut = t[:limit - 1]
        # 优先在标点处断句：硬切会把 "__name__" 切成 "__n…"
        idx = max(cut.rfind(c) for c in "，。；、,;:：")
        if idx >= limit * 0.5:
            cut = cut[:idx]
        t = cut.rstrip("，。；、,;:： ") + "…"
    return t


def esc_attr(t):
    """放进 JSX 单引号字符串里：转义单引号与反斜杠。"""
    return esc(t).replace("\\", "\\\\").replace("'", "\\'")


def md_of(unit):
    for f in os.listdir(COURSE):
        if f.startswith(f"{unit:02d}-"):
            return open(os.path.join(COURSE, f), encoding="utf-8").read()
    return ""


def slice_md(md, start, end):
    lines = md.split("\n")

    def find(title):
        if title is None:
            return len(lines)
        for i, l in enumerate(lines):
            if l.strip().startswith("#"):
                t = re.sub(r"^#+\s*", "", l).strip()
                if t == title or t.startswith(title):
                    return i
        return None

    a, b = find(start), find(end)
    return "\n".join(lines[a:b]) if a is not None and b is not None else ""


def knowledge_points(frag, max_blocks=4, max_bullets=3):
    """按 h3 切块，取「标题 + 头几条要点」。"""
    out = []
    blocks = re.split(r"^###\s+", frag, flags=re.M)[1:]
    for b in blocks:
        # 先把代码块整段剔掉：兜底分支按「段落」取要点时，
        # 代码里的 print(...) 会被当成一句话塞进卡片（踩过）。
        b = re.sub(r"^```.*?^```", "", b, flags=re.S | re.M)
        lines = b.split("\n")
        head = esc(lines[0], 30)
        if not head or head.startswith("示例"):
            continue
        bullets = []
        for l in lines[1:]:
            s = l.strip()
            if s.startswith(("- ", "* ")) and len(s) > 8:
                bullets.append(esc(s[2:], 52))
            elif re.match(r"^\*\*[^*]{4,}\*\*", s):
                # 只取粗体那半句当要点：整段（含解释）塞进卡片会被排版截断成 "__n…"
                m2 = re.match(r"^\*\*([^*]{4,})\*\*", s)
                bold = m2.group(1)
                # 以冒号收尾的是「引导句」（下面才讲），当要点等于什么也没说
                if not bold.rstrip().endswith(("：", ":")):
                    bullets.append(esc(bold, 52))
            if len(bullets) >= max_bullets:
                break
        if not bullets:
            # 兜底：没有列表也没有粗体，就从段落里取「第一句」。
            # 两条规则是踩出来的：
            #   ① 以冒号收尾的段落是引导句（「这是一个很优雅的结构：」），跳过去看下一段；
            #   ② 一句不够，要取到 max_bullets 条，只取一条时卡片里会只剩半句话。
            for l in lines[1:]:
                s = l.strip()
                if not s or s.startswith(("#", "```", "|", ">", "!", "~~~")):
                    continue
                if s.rstrip().endswith(("：", ":")):
                    continue
                first = re.split(r"(?<=[。！？])", s)[0].strip() or s
                # 去掉「生活化类比：」「一句话：」这类前缀——前缀不是信息，
                # 占着卡片一行反而挤掉了真正的内容。
                first = re.sub(r"^[^，。；]{2,8}[：:]\s*", "", first) or first
                first = first.strip("*_ ")
                if len(first) < 12:
                    continue
                bullets.append(esc(first, 52))
                if len(bullets) >= max_bullets:
                    break
        if bullets:
            out.append((head, bullets))
        if len(out) >= max_blocks:
            break
    return out


def examples_of(frag, limit=4):
    ex = re.findall(r"^###\s*示例\s*\d+[：:]\s*(.*)$", frag, re.M)
    return [esc(e, 34) for e in ex][:limit]



def wrap_cjk(text, max_chars, max_lines=99):
    """按「字符数」折行（中文按 1 个宽度算，英文数字按 0.55 计）。

    返回行列表。超出 max_lines 时最后一行加省略号。
    """
    def width(ch):
        return 0.55 if ord(ch) < 128 else 1.0

    text = esc(text)
    BREAKERS = " ，。；、,;:："
    lines, cur, w = [], "", 0.0
    for ch in text:
        cw = width(ch)
        if w + cw > max_chars and cur:
            # 能在空格/标点处断就别硬切：硬切会把 scores.get 断成 "g" + "et)"
            idx = max(cur.rfind(c) for c in BREAKERS)
            if idx >= max(2, int(len(cur) * 0.45)):
                head, tail = cur[:idx + 1], cur[idx + 1:]
            else:
                head, tail = cur, ""
            lines.append(head.rstrip())
            cur, w = tail, sum(width(c) for c in tail)
        cur += ch
        w += cw
    if cur:
        lines.append(cur)
    # 行首的收尾标点并回上一行，避免一行只有一个「；」
    tidy = []
    for ln in lines:
        if tidy and ln and ln[0] in "；。，、,;:：）":
            tidy[-1] += ln[0]
            ln = ln[1:]
        if ln:
            tidy.append(ln)
    lines = tidy
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][:-1] + "…"
    return lines or [""]


def svg_text(x, y, lines, size=14, color="#3A4A58", bold=False,
             line_h=22, prefix="", anchor="start"):
    """把多行文本渲染成多个 <text>。"""
    out = []
    for i, ln in enumerate(lines):
        fw = " fontWeight='bold'" if bold else ""
        out.append(
            f"<text x='{x}' y='{y + i * line_h}' fontSize='{size}'{fw} "
            f"fill='{color}' textAnchor='{anchor}' fontFamily='{CJK}'>"
            f"{prefix if i == 0 else ''}{ln}</text>")
    return "".join(out)



def bullets_svg(x, y, items, avail_w, fs=14.5, max_items=3, max_lines=2,
                color="#3A4A58"):
    """把若干条要点渲染成自动折行的 <text> 组，返回 (svg, 结束 y)。"""
    out, cy = [], y
    maxc = max(8, int(avail_w / fs))
    for it in items[:max_items]:
        lines = wrap_cjk(it, maxc, max_lines=max_lines)
        out.append(svg_text(x, cy, lines, size=fs, color=color,
                            line_h=fs * 1.5, prefix="· "))
        cy += len(lines) * fs * 1.5 + 9
    return "".join(out), cy


# ── Slide 模板 ──
def slide_cover(unit, unit_title, lessons, week):
    """单元封面：标题 + 本单元课节清单 + 产出物。"""
    rows = []
    y = 196
    for i, (n, t) in enumerate(lessons):
        rows.append(
            f"<rect x='0' y='{y}' width='1152' height='38' rx='7' "
            f"fill='{'#FFFFFF' if i % 2 == 0 else '#F2F7FD'}' />")
        rows.append(
            f"<text x='16' y='{y + 25}' fontSize='15' fontWeight='bold' "
            f"fill='{P1}' fontFamily='{CJK}'>第 {n} 节</text>")
        rows.append(
            f"<text x='96' y='{y + 25}' fontSize='15' fill='{INK}' "
            f"fontFamily='{CJK}'>{esc(t, 40)}</text>")
        rows.append(
            f"<text x='1080' y='{y + 25}' fontSize='13' fill='{MUTED}' "
            f"textAnchor='end' fontFamily='{CJK}'>{esc(week)}</text>")
        y += 42
    title2 = esc(unit_title, 22)
    return f"""<Slide style={{{{ width: '1280px', height: '720px', backgroundColor: '{BG}', padding: 0, position: 'relative', overflow: 'hidden' }}}}>
    <Box style={{{{ position: 'absolute', left: 0, top: 0, width: '1280px', height: '150px', background: '{P1}' }}}} />
    <Box style={{{{ position: 'absolute', left: 64, top: 34, width: '1152px', flexDirection: 'column' }}}}>
        <Text style={{{{ fontSize: 15, fontWeight: 'bold', color: '#BFD9F2', letterSpacing: 2 }}}}>阶段 {pm.STAGE_OF.get(unit, 1) if hasattr(pm, 'STAGE_OF') else (1 if unit <= 11 else 2)} · 单元 {unit}</Text>
        <Text style={{{{ fontSize: 38, fontWeight: 'bold', color: '#FFFFFF', marginTop: 6 }}}}>{title2}</Text>
    </Box>
    <Box style={{{{ position: 'absolute', left: 64, top: 168, width: '1152px', height: 470 }}}}>
        <svg width='1152' height='470' viewBox='0 0 1152 470'>
            <text x='0' y='18' fontSize='15' fontWeight='bold' fill='{INK}' fontFamily='{CJK}'>本单元共 {len(lessons)} 节课</text>
            {''.join(rows)}
        </svg>
    </Box>
    <Box style={{{{ position: 'absolute', left: 64, bottom: 22, width: '1152px', flexDirection: 'row', justifyContent: 'space-between' }}}}>
        <Text style={{{{ fontSize: 13, color: '#8A9AAA' }}}}>Python 讲授课件 · 逐节版</Text>
        <Text style={{{{ fontSize: 13, color: '#8A9AAA' }}}}>单元 {unit} · 封面</Text>
    </Box>
</Slide>
"""


def slide_lesson(unit, n, title, goal, live, hw):
    """课节页：学习目标 + 课堂实操 + 课后作业（整页 SVG，页面坐标）。"""
    p = []
    # 学习目标卡
    p.append(f"<rect x='64' y='104' width='1152' height='112' rx='12' fill='#EEF5FB' />")
    p.append(svg_text(84, 134, ["学习目标"], size=15, color=P1, bold=True))
    p.append(svg_text(84, 164, wrap_cjk(goal, 72, max_lines=2), size=16,
                      color="#243444", line_h=25))

    for x, fill, stroke, head, items, hc in (
            (64, "#FFFFFF", LINE, "课堂实操（40 分钟 · 不看答案）", live, P2),
            (654, "#FDF3E2", "none", "课后作业", hw, P3)):
        p.append(f"<rect x='{x}' y='240' width='562' height='248' rx='12' "
                 f"fill='{fill}' stroke='{stroke}' />")
        p.append(svg_text(x + 20, 274, [head], size=15, color=hc, bold=True))
        body, _ = bullets_svg(x + 20, 308, items, 522)
        p.append(body)

    p.append(f"<rect x='64' y='508' width='1152' height='92' rx='12' fill='#16232E' />")
    p.append(svg_text(84, 540, ["这节课的节奏"], size=14.5, color="#FFFFFF",
                      bold=True))
    p.append(svg_text(84, 570, ["先读讲义 20 分钟 → 自己敲 40 分钟（报错先自己读）"
                                " → 对着讲评自查 20 分钟 → 写作业 10 分钟"],
                      size=14, color="#A8C4DE"))
    return f"""<Slide style={{{{ width: '1280px', height: '720px', backgroundColor: '{BG}', padding: 0, position: 'relative', overflow: 'hidden' }}}}>
    <Box style={{{{ position: 'absolute', left: 64, top: 36, width: '1152px', flexDirection: 'row', alignItems: 'center', gap: 12 }}}}>
        <Box style={{{{ background: '{P1}', borderRadius: 5, padding: '3px 11px' }}}}>
            <Text style={{{{ fontSize: 14, fontWeight: 'bold', color: '#FFFFFF' }}}}>第 {n} / {TOTAL_LESSONS} 节</Text>
        </Box>
        <Text style={{{{ fontSize: 30, fontWeight: 'bold', color: '{INK}' }}}}>{esc(title, 28)}</Text>
    </Box>
    <Box style={{{{ position: 'absolute', left: 0, top: 0, width: '1280px', height: '720px' }}}}>
        <svg width='1280' height='720' viewBox='0 0 1280 720'>
            {''.join(p)}
            <text x='64' y='684' fontSize='13' fill='#8A9AAA' fontFamily='{CJK}'>Python 讲授课件 · 逐节版</text>
            <text x='1216' y='684' fontSize='13' fill='#8A9AAA' textAnchor='end' fontFamily='{CJK}'>单元 {unit} · 第 {n} 节</text>
        </svg>
    </Box>
</Slide>
"""


def slide_points(unit, n, title, points, examples):
    """知识点页：最多 3 个要点块 + 代码示例（整页 SVG，页面坐标）。"""
    p = []
    pts = points[:3]
    geo = {1: (64, 0, 1152), 2: (64, 604, 548), 3: (64, 404, 368)}.get(
        len(pts), (64, 404, 368))
    x0, dx, w = geo
    inner = w - 36
    for i, (head, bullets) in enumerate(pts):
        x = x0 + i * dx
        p.append(f"<rect x='{x}' y='96' width='{w}' height='330' rx='12' "
                 f"fill='#FFFFFF' stroke='{LINE}' />")
        p.append(f"<rect x='{x}' y='96' width='{w}' height='4' rx='2' fill='{P1}' />")
        hl = wrap_cjk(head, max(10, int(inner / 15.5)), max_lines=2)
        p.append(svg_text(x + 18, 130, hl, size=15.5, color=P1, bold=True,
                          line_h=23))
        body, _ = bullets_svg(x + 18, 130 + len(hl) * 23 + 16, bullets, inner,
                              fs=13, max_items=3, max_lines=3)
        p.append(body)
    if examples:
        ex = examples[:3]
        exdx = {1: 0, 2: 604, 3: 404}.get(len(ex), 404)
        exw = {1: 1152, 2: 548, 3: 368}.get(len(ex), 368) - 36
        p.append(svg_text(64, 470, ["本节的代码示例"], size=14.5, color=P2,
                          bold=True))
        for j, e in enumerate(ex):
            p.append(svg_text(64 + j * exdx, 500,
                              wrap_cjk(e, max(10, int(exw / 13)), max_lines=1),
                              size=13, prefix="· "))
    p.append(f"<rect x='64' y='574' width='1152' height='66' rx='12' fill='#EEF5FB' />")
    p.append(svg_text(84, 616, ["看不懂的地方先回讲义对应小节读一遍，"
                                "再回来对着这页复述一次——能讲出来才算真懂。"],
                      size=14, color="#243444"))
    return f"""<Slide style={{{{ width: '1280px', height: '720px', backgroundColor: '{BG}', padding: 0, position: 'relative', overflow: 'hidden' }}}}>
    <Box style={{{{ position: 'absolute', left: 64, top: 36, width: '1152px', flexDirection: 'row', alignItems: 'center', gap: 12 }}}}>
        <Box style={{{{ background: '{P2}', borderRadius: 5, padding: '3px 11px' }}}}>
            <Text style={{{{ fontSize: 14, fontWeight: 'bold', color: '#FFFFFF' }}}}>第 {n} 节</Text>
        </Box>
        <Text style={{{{ fontSize: 30, fontWeight: 'bold', color: '{INK}' }}}}>核心知识点</Text>
        <Text style={{{{ fontSize: 15, color: '{MUTED}', marginTop: 10 }}}}>· {esc(title, 22)}</Text>
    </Box>
    <Box style={{{{ position: 'absolute', left: 0, top: 0, width: '1280px', height: '720px' }}}}>
        <svg width='1280' height='720' viewBox='0 0 1280 720'>
            {''.join(p)}
            <text x='64' y='684' fontSize='13' fill='#8A9AAA' fontFamily='{CJK}'>Python 讲授课件 · 逐节版</text>
            <text x='1216' y='684' fontSize='13' fill='#8A9AAA' textAnchor='end' fontFamily='{CJK}'>单元 {unit} · 第 {n} 节</text>
        </svg>
    </Box>
</Slide>
"""


def slide_summary(unit, unit_title, lessons, n_slides):
    items = "".join(
        f"<text x='0' y='{34 + i * 30}' fontSize='14.5' fill='#3A4A58' "
        f"fontFamily='{CJK}'>· 第 {n} 节 · {esc(t, 34)}</text>"
        for i, (n, t) in enumerate(lessons))
    return f"""<Slide style={{{{ width: '1280px', height: '720px', backgroundColor: '{BG}', padding: 0, position: 'relative', overflow: 'hidden' }}}}>
    <Box style={{{{ position: 'absolute', left: 0, top: 0, width: '12px', height: '720px', background: '{P2}' }}}} />
    <Box style={{{{ position: 'absolute', left: 72, top: 44, width: '1144px', flexDirection: 'column' }}}}>
        <Text style={{{{ fontSize: 34, fontWeight: 'bold', color: '{INK}' }}}}>单元 {unit} · 小结与验收</Text>
        <Text style={{{{ fontSize: 16, color: '{MUTED}', marginTop: 6 }}}}>{esc(unit_title, 30)}</Text>
    </Box>
    <Box style={{{{ position: 'absolute', left: 72, top: 148, width: '552px', height: 400, background: '#FFFFFF', border: '1px solid {LINE}', borderRadius: 12, padding: 18, flexDirection: 'column' }}}}>
        <Text style={{{{ fontSize: 16, fontWeight: 'bold', color: '{P1}' }}}}>本单元课节回顾</Text>
        <Box style={{{{ marginTop: 10, position: 'relative', height: 330 }}}}>
            <svg width='516' height='330' viewBox='0 0 516 330'>{items}</svg>
        </Box>
    </Box>
    <Box style={{{{ position: 'absolute', left: 656, top: 148, width: '560px', height: 400, background: '#FDF3E2', borderRadius: 12, padding: 20, flexDirection: 'column' }}}}>
        <Text style={{{{ fontSize: 16, fontWeight: 'bold', color: '{P3}' }}}}>过关标准</Text>
        <Text style={{{{ fontSize: 15, color: '#3A4A58', marginTop: 12, lineHeight: 1.9 }}}}>
            1. 本单元每一节的课后作业都做完并自己验收过{chr(10)}
            2. 不看讲义能独立重写一遍本单元的示例代码{chr(10)}
            3. 讲义最后「本单元验收自测」全部答对{chr(10)}
            4. 产出物已经写进笔记或提交到 Git
        </Text>
        <Text style={{{{ fontSize: 14, color: '#8A6A2A', marginTop: 16, lineHeight: 1.7 }}}}>
            没过关的项回到对应那一节重做，不要整体重学。
        </Text>
    </Box>
    <Box style={{{{ position: 'absolute', left: 72, bottom: 26, width: '1144px', flexDirection: 'row', justifyContent: 'space-between' }}}}>
        <Text style={{{{ fontSize: 13, color: '#8A9AAA' }}}}>Python 讲授课件 · 逐节版</Text>
        <Text style={{{{ fontSize: 13, color: '#8A9AAA' }}}}>单元 {unit} · 小结</Text>
    </Box>
</Slide>
"""


def build_unit_slides(unit):
    """生成某单元的全部 slide DSL，返回 (slides, meta)。"""
    md = md_of(unit)
    ls = [(i + 1, L) for i, L in enumerate(bl.LESSONS) if L[0] == unit]
    unit_title = bl.TITLES[unit] if hasattr(bl, "TITLES") else ""
    if not unit_title:
        import lesson_tpl
        unit_title = lesson_tpl.UNIT_TITLE.get(unit, f"单元 {unit}")

    lessons = [(n, L[3]) for n, L in ls]
    week = ls[0][1][2] if ls else ""

    out = [("cover", slide_cover(unit, unit_title, lessons, week))]
    meta = [{"kind": "cover", "title": f"单元 {unit} · {unit_title}",
             "lessons": []}]
    for n, L in ls:
        _, (start, end), wk, title, goal, live, hw = L
        frag = slice_md(md, start, end)
        pts = knowledge_points(frag)
        exs = examples_of(frag)
        out.append(("lesson", slide_lesson(unit, n, title, goal, live, hw)))
        meta.append({"kind": "lesson", "no": n, "title": title})
        out.append(("points", slide_points(unit, n, title, pts, exs)))
        meta.append({"kind": "points", "no": n, "title": title})
    out.append(("summary", slide_summary(unit, unit_title, lessons, len(out) + 1)))
    meta.append({"kind": "summary", "title": f"单元 {unit} · 小结"})
    return out, meta
