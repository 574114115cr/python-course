# -*- coding: utf-8 -*-
"""全站深浅配色的唯一来源：浅色样式表 → 深色样式表（自动派生）。

为什么这样做
------------
以前深色模式是「手写补丁」：在 CSS 末尾加一段
`@media (prefers-color-scheme: dark){ .某块{background:#1a2632} }`。
问题是只要新写了一个块、或者某块在浅色里写死了底色，深色下就会留一块刺眼的
白底或看不清的深字 —— 补丁永远漏，用户就只能自己去发现。

这里换成「极性变换」：拿浅色样式表当唯一来源，构建时生成一份等价的深色表：

  * 浅色表面（HSL 亮度 >= 0.60 的 background / border 颜色）
    → 按亮度映射到深色表面色阶（保留色相，饱和度压到 0.30，卡片比页面底浅一档）；
  * 深色墨色（color / --* 变量里亮度 < 0.60 的颜色）
    → 提亮到 0.60~0.91，色相不变；饱和度高的（>=0.45，通常是强调色）只提一档；
  * 本来就是深色的表面（代码块的 Monokai 底、品牌渐变）原样保留。

于是「写死的颜色」不再是漏洞：它在浅色里是什么语义，深色里就自动跟着翻。

同时提供主题切换：
  * `<html data-theme="dark">` / `[data-theme="light"]` 驱动，`color-scheme` 同步
    （让原生滚动条、下拉框、日期控件也变深）；
  * head 里一段同步脚本先落属性，避免刷新时白闪；
  * 顶栏注入一个可见的切换按钮（跟随系统 → 浅色 → 深色 三态循环），
    选择存 localStorage `py-theme-v1`，全站共用。

对外接口
--------
theme.css(sheet)      -> 浅色表 + 深色表（带 /*@theme-dark*/ 标记，可重复调用）
theme.inject(html)    -> 处理页面里所有 <style>，并注入脚本/按钮/样式
theme.write(path, s)  -> 按扩展名处理 html / css 后写盘
theme.sweep(dirs)     -> 目录内批量处理（构建后兜底）
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CSS_MARK = "/*@theme-dark*/"
HEAD_BEGIN = "<!--@theme:head-->"
HEAD_END = "<!--/@theme:head-->"
BODY_BEGIN = "<!--@theme:body-->"
BODY_END = "<!--/@theme:body-->"

# ── 变换参数（改这几个数就能整体调深色的明暗，不用逐条改颜色） ────────────────
SURF_MIN_L = 0.60      # 亮度 >= 此值算「浅色表面」，要翻成深色
SURF_S = 0.30          # 深色表面的统一饱和度（保留色相，避免脏色）
INK_MAX_L = 0.60       # 亮度 < 此值算「深色墨色」，要提亮
INK_L_TOP = 0.91       # 正文墨色提亮上限
INK_S_MAX = 0.72       # 提亮后饱和度上限
ACCENT_S = 0.45        # 饱和度高于此值视为强调色，只提一档
ACCENT_L_TOP = 0.70    # 强调色提亮上限（0.70 是能压住 4.5:1 的下限附近）
GREY_H = 210           # 近灰色统一采用的色相（和 --line/--card 的蓝灰一致）

# 深色表的挂载点：根选择器要高权重才能压过 :root 的变量；
# 普通选择器用 :where() 包成 0 权重，保持原本的相对优先级不被搅乱。
SCOPE_STRONG = 'html[data-theme="dark"]'
SCOPE_WEAK = ':where(html[data-theme="dark"])'

# 深色端的亮度台阶：(浅色亮度, 深色亮度)。表面和描边分开两张表——
# 浅色里描边比卡片暗、深色里必须比卡片亮，否则边框会整片消失（这是最容易踩的坑）。
SURF_RAMP = [(1.00, 0.128), (0.985, 0.104), (0.95, 0.100), (0.90, 0.096),
             (0.80, 0.092), (0.60, 0.088)]
DIV_RAMP = [(1.00, 0.240), (0.95, 0.228), (0.90, 0.215), (0.85, 0.203),
            (0.75, 0.190), (0.60, 0.176)]

COLOR_RE = re.compile(
    r"#[0-9a-fA-F]{8}\b|#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3,4}\b"
    r"|rgba?\([^()]*\)|hsla?\([^()]*\)"
)
INK_PROPS = {"color", "caret-color", "text-decoration-color",
             "-webkit-text-fill-color", "text-emphasis-color"}
DIV_PREFIX = ("border", "outline", "column-rule")
SURF_PREFIX = ("background",)     # 阴影/图标填充一律不动：它们本来就该是深色或高亮
SKIP_VALUE = ("url(", "currentcolor", "inherit", "initial", "unset")
# 强调色变量：会被提亮，但同时要留一份「原色」给它当实心底色用（白字压在上面才够黑）
ACCENT_VAR_RE = re.compile(r"^--(p\d+|danger)$")
VAR_DIV_WORDS = ("line", "border", "divider", "rule", "split")


# ── 颜色工具 ────────────────────────────────────────────────────────────────
def _clamp(v, lo, hi):
    return lo if v < lo else (hi if v > hi else v)


def hex_to_rgb(s):
    s = s.lstrip("#")
    if len(s) in (3, 4):
        s = "".join(c * 2 for c in s[:3])
    elif len(s) >= 6:
        s = s[:6]
    else:
        return None
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hsl(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mx, mn = max(r, g, b), min(r, g, b)
    l = (mx + mn) / 2
    d = mx - mn
    if d < 1e-9:
        return 0.0, 0.0, l
    s = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)
    if mx == r:
        h = ((g - b) / d) % 6
    elif mx == g:
        h = (b - r) / d + 2
    else:
        h = (r - g) / d + 4
    return h * 60, s, l


def hsl_to_rgb(h, s, l):
    h = h % 360
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2
    seg = int(h // 60) % 6
    r, g, b = [(c, x, 0), (x, c, 0), (0, c, x),
               (0, x, c), (x, 0, c), (c, 0, x)][seg]
    return (round((r + m) * 255), round((g + m) * 255), round((b + m) * 255))


def hsl_to_hex(h, s, l):
    r, g, b = hsl_to_rgb(h, s, l)
    return "#%02x%02x%02x" % (r, g, b)


def _parse_color(tok):
    """-> (r,g,b,a) 或 None"""
    t = tok.strip().lower()
    if t.startswith("#"):
        v = hex_to_rgb(t)
        if not v:
            return None
        a = 1.0
        s = t.lstrip("#")
        if len(s) in (4, 8):
            a = int(s[-1] * 2, 16) / 255.0
        return v[0], v[1], v[2], a
    m = re.match(r"rgba?\(([^)]*)\)", t)
    if m:
        parts = [p.strip() for p in re.split(r"[,\s/]+", m.group(1)) if p.strip()]
        if len(parts) < 3:
            return None
        vals = []
        for p in parts[:3]:
            vals.append(round(float(p[:-1]) * 255 / 100) if p.endswith("%")
                        else round(float(p)))
        a = 1.0
        if len(parts) >= 4:
            a = float(parts[3][:-1]) / 100 if parts[3].endswith("%") else float(parts[3])
        return vals[0], vals[1], vals[2], a
    m = re.match(r"hsla?\(([^)]*)\)", t)
    if m:
        parts = [p.strip() for p in re.split(r"[,\s/]+", m.group(1)) if p.strip()]
        if len(parts) < 3:
            return None
        h = float(parts[0].replace("deg", ""))
        s = float(parts[1].rstrip("%")) / 100
        l = float(parts[2].rstrip("%")) / 100
        a = 1.0
        if len(parts) >= 4:
            a = float(parts[3][:-1]) / 100 if parts[3].endswith("%") else float(parts[3])
        r, g, b = hsl_to_rgb(h, s, l)
        return r, g, b, a
    return None


def _fmt(r, g, b, a):
    if a >= 0.999:
        return "#%02x%02x%02x" % (r, g, b)
    return "rgba(%d,%d,%d,%s)" % (r, g, b, ("%.3f" % a).rstrip("0").rstrip("."))


def rel_lum(r, g, b):
    def f(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def to_solid(r, g, b, a):
    """实心底色（上面压白字的那些徽标）：压暗到白字仍有 4.5:1。"""
    if rel_lum(r, g, b) <= 0.155:
        return None                       # 本来就够深，保持原色
    h, s, l = rgb_to_hsl(r, g, b)
    lo, hi = 0.0, l
    for _ in range(20):
        mid = (lo + hi) / 2
        if rel_lum(*hsl_to_rgb(h, s, mid)) <= 0.145:
            lo = mid
        else:
            hi = mid
    r2, g2, b2 = hsl_to_rgb(h, s, lo)
    return r2, g2, b2, a


def _ramp(l, table):
    if l <= table[-1][0]:
        return table[-1][1]
    if l >= table[0][0]:
        return table[0][1]
    for i in range(len(table) - 1):
        hi, lo = table[i], table[i + 1]
        if lo[0] <= l <= hi[0]:
            t = (l - lo[0]) / (hi[0] - lo[0])
            return lo[1] + t * (hi[1] - lo[1])
    return table[-1][1]


def to_surface(r, g, b, a, role="surface"):
    """浅色表面 / 描边 → 深色。"""
    h, s, l = rgb_to_hsl(r, g, b)
    if l < SURF_MIN_L:
        return None                      # 本来就是深色，别动（代码块底、品牌渐变）
    l2 = _ramp(l, DIV_RAMP if role == "divider" else SURF_RAMP)
    s2 = SURF_S if s >= 0.04 else SURF_S * 0.86
    h2 = h if s >= 0.04 else GREY_H
    r2, g2, b2 = hsl_to_rgb(h2, s2, l2)
    return r2, g2, b2, a


def to_ink(r, g, b, a):
    """深色墨色 → 浅色墨色。"""
    h, s, l = rgb_to_hsl(r, g, b)
    if l >= INK_MAX_L:
        return None                      # 本来就浅，别动
    if s >= ACCENT_S:                    # 强调色：保持鲜艳，但也要够亮才压得住 4.5:1
        l2 = min(INK_MAX_L + (INK_MAX_L - l) * 0.42, ACCENT_L_TOP)
        s2 = min(s, 0.78)
    else:
        l2 = min(INK_MAX_L + (INK_MAX_L - l) * 0.62, INK_L_TOP)
        s2 = min(s, INK_S_MAX)
    r2, g2, b2 = hsl_to_rgb(h, s2, l2)
    return r2, g2, b2, a


def _map_value(value, role):
    def rep(m):
        c = _parse_color(m.group(0))
        if not c:
            return m.group(0)
        r, g, b, a = c
        if role == "ink":
            out = to_ink(r, g, b, a)
        elif role in ("surface", "divider"):
            out = to_surface(r, g, b, a, role)
            # 中间调（既不是浅底也不是深底）当底色时，浅色主题里常常压着白字，
            # 深色下原样保留会只剩 2~3:1，所以继续压到「白字够读」为止。
            if out is None and role == "surface":
                out = to_solid(r, g, b, a)
        else:                            # 变量：按亮度猜语义
            out = to_ink(r, g, b, a) if rgb_to_hsl(r, g, b)[2] < INK_MAX_L \
                else to_surface(r, g, b, a, "surface")
        if not out:
            return m.group(0)
        return _fmt(*out)
    return COLOR_RE.sub(rep, value)


def _solid_accent(value):
    """`var(--p1)` 这种「整块当实心底色」的值 → 换成原色版 var(--p1s)。

    强调色在深色下会被提亮（浅蓝字才看得清），但同一个变量也常被当成
    按钮/圆标的底色、上面压白字；提亮后白字就糊了。所以深色表里给每个
    强调色再存一份原色 --p1s，实心底色的位置改用它。
    """
    m = re.match(r"^var\(\s*(--[a-z0-9-]+)\s*\)$", value.strip(), re.I)
    if not m:
        return None
    if not ACCENT_VAR_RE.match(m.group(1)):
        return None
    return "var(%ss)" % m.group(1)


def _transform_decls(decls):
    out = []
    for part in _split_decls(decls):
        if ":" not in part:
            if part.strip():
                out.append(part.strip())
            continue
        prop, _, value = part.partition(":")
        prop = prop.strip()
        low = prop.lower()
        v = value.strip()
        vlow = v.lower()
        if low.startswith("--"):
            # 自定义属性：先看名字（--line/--border 是描边），再看亮度判语义；
            # 强调色额外留一份原色给实心底色用
            m = COLOR_RE.fullmatch(v)
            if m:
                c = _parse_color(m.group(0))
                if any(w in low for w in VAR_DIV_WORDS):
                    role = "divider"
                else:
                    role = "ink" if rgb_to_hsl(*c[:3])[2] < INK_MAX_L else "surface"
                out.append(f"{prop}:{_map_value(v, role)}")
                if ACCENT_VAR_RE.match(low):
                    solid = to_solid(*c)
                    out.append(f"{prop}s:{_fmt(*solid) if solid else v}")
            else:
                out.append(f"{prop}:{v}")
            continue
        if any(k in vlow for k in SKIP_VALUE):
            out.append(f"{prop}:{v}")
            continue
        if low in INK_PROPS:
            out.append(f"{prop}:{_map_value(v, 'ink')}")
            continue
        if low.startswith(DIV_PREFIX):
            role = "divider"
        elif low.startswith(SURF_PREFIX):
            role = "surface"
        else:
            out.append(f"{prop}:{v}")
            continue
        solid = _solid_accent(v) if role == "surface" else None
        out.append(f"{prop}:{solid or _map_value(v, role)}")
    return ";".join(out)


def _split_decls(decls):
    """按分号切声明，跳过括号/引号内的分号。"""
    parts, buf, depth, quote = [], [], 0, None
    for ch in decls:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            buf.append(ch)
        elif ch == "(":
            depth += 1
            buf.append(ch)
        elif ch == ")":
            depth -= 1
            buf.append(ch)
        elif ch == ";" and depth == 0:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if buf:
        parts.append("".join(buf))
    return parts


# ── CSS 解析 / 输出 ─────────────────────────────────────────────────────────
def _read_block(css, i):
    """i 指向 '{'，返回 (块内文本, 块后下标)。"""
    assert css[i] == "{"
    depth, quote, j = 0, None, i
    while j < len(css):
        ch = css[j]
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return css[i + 1:j], j + 1
        j += 1
    return css[i + 1:], len(css)


def parse_css(css):
    """-> 节点列表：('rule', selectors, decls) / ('at', prelude, nodes) / ('raw', text)"""
    nodes, i, n = [], 0, len(css)
    while i < n:
        ch = css[i]
        if ch in " \t\r\n;":
            i += 1
            continue
        if css.startswith("/*", i):
            j = css.find("*/", i + 2)
            i = n if j < 0 else j + 2
            continue
        if ch == "@":
            j = i
            while j < n and css[j] not in "{;":
                j += 1
            if j >= n:
                break
            if css[j] == ";":
                nodes.append(("raw", css[i:j + 1].strip()))
                i = j + 1
                continue
            prelude = css[i:j].strip()
            body, i = _read_block(css, j)
            m = re.match(r"@([-\w]+)", prelude)
            name = m.group(1).lower() if m else ""
            if name in ("media", "supports", "container", "layer", "document"):
                nodes.append(("at", prelude, parse_css(body)))
            else:
                nodes.append(("raw", prelude + "{" + body + "}"))
            continue
        j = css.find("{", i)
        if j < 0:
            break
        sel = css[i:j].strip()
        body, i = _read_block(css, j)
        nodes.append(("rule", sel, body))
    return nodes


def _prefix_selector(sel, prefix):
    out = []
    for one in sel.split(","):
        one = one.strip()
        if not one:
            continue
        low = one.lower()
        if low == ":root" or low == "html" or low.startswith("html[") \
                or low.startswith("html.") or low.startswith("html:"):
            out.append(prefix + one[len("html"):] if low != ":root" else prefix)
        else:
            # 用 :where() 把外层包成 0 优先级：否则深色表里每条规则都白白多一层权重，
            # 会把 .fld.scb 这类更具体的浅色规则压掉（边框/底色错位，很难查）。
            out.append(SCOPE_WEAK + " " + one)
    return ",".join(out)


def _emit_dark(nodes, prefix):
    chunks = []
    for node in nodes:
        if node[0] == "rule":
            _, sel, decls = node
            new = _transform_decls(decls)
            if new.strip():
                chunks.append(_prefix_selector(sel, prefix) + "{" + new + "}")
        elif node[0] == "at":
            _, prelude, kids = node
            if re.search(r"\bprint\b", prelude, re.I):
                continue                 # 打印一律用浅色表：深色表不进 print，省墨也好读
            inner = _emit_dark(kids, prefix)
            if inner.strip():
                chunks.append(prelude + "{\n" + inner + "\n}")
        else:
            chunks.append(node[1])      # @keyframes / @font-face 原样
    return "\n".join(chunks)


def _strip_old_dark(css):
    """删掉历史上手写的 @media (prefers-color-scheme: dark) 块（已被派生表取代）。"""
    out, i, n = [], 0, len(css)
    pat = re.compile(r"@media[^{]*prefers-color-scheme\s*:\s*dark[^{]*\{", re.I)
    while i < n:
        m = pat.search(css, i)
        if not m:
            out.append(css[i:])
            break
        out.append(css[i:m.start()])
        _, i = _read_block(css, m.end() - 1)
        out.append("\n")
    return "".join(out)


def _strip_generated(css):
    """去掉上一次生成的深色表（保证可重复执行）。"""
    i = css.find(CSS_MARK)
    return css[:i] if i >= 0 else css


def _dark_body(css):
    return _emit_dark(parse_css(css), SCOPE_STRONG)


def css(sheet, want_dark=True):
    """浅色样式表 → 浅色 + 派生深色。"""
    light = _strip_generated(_strip_old_dark(sheet)).rstrip()
    if not want_dark:
        return light + "\n"
    dark = _dark_body(light)
    return light + "\n" + CSS_MARK + "\n" + dark + "\n"


# ── 页面注入：脚本 / 按钮 / 基础样式 ────────────────────────────────────────
HEAD_JS = """<script>(function(){var m='auto';try{m=localStorage.getItem('py-theme-v1')||'auto'}catch(e){}if(m!=='light'&&m!=='dark')m='auto';var q=window.matchMedia&&window.matchMedia('(prefers-color-scheme:dark)');var d=m==='dark'||(m==='auto'&&q&&q.matches);var r=document.documentElement;r.setAttribute('data-theme-mode',m);r.setAttribute('data-theme',d?'dark':'light');})();</script>"""

BASE_CSS = """<style>
/* 主题切换按钮 + 原生控件配色（由 tools/theme.py 注入，勿手改） */
html[data-theme="dark"]{color-scheme:dark}
html[data-theme="light"]{color-scheme:light}
/* 强调色的「原色版」：浅色下等于强调色本身，深色下由派生表换成压暗后的实心底色。
   凡是把强调色当实心底、上面压白字的地方都用 --p1s 这类变量（否则白字会糊）。 */
:root{--bg:#f6f8fb;--card:#fff;--line:#e3e8ef;--text:#16232e;--muted:#5f7183;--p1:#1f5fa8;
--p1s:var(--p1);--p2s:var(--p2);--p3s:var(--p3);--p4s:var(--p4);--dangers:var(--danger)}
html[data-theme="dark"]{--bg:#0f1620;--card:#16202b;--line:#243342;--text:#e6edf5;
--muted:#93a6b8;--p1:#63a9ee}
body{transition:background-color .18s,color .18s}
::selection{background:rgba(99,169,238,.32)}
.thbtn{display:inline-flex;align-items:center;gap:6px;height:30px;padding:0 10px;
border-radius:999px;border:1px solid var(--line);background:var(--card);color:var(--muted);
font:inherit;font-size:12.5px;font-weight:700;line-height:1;cursor:pointer;
white-space:nowrap;flex:0 0 auto}
.thbtn:hover{color:var(--text);border-color:var(--p1)}
.thbtn:focus-visible{outline:2px solid var(--p1);outline-offset:2px}
.thbtn .thi svg{width:15px;height:15px;display:block}
.thbtn .thlbl{display:inline}
/* 窄屏顶栏本来就挤（返回 / 标题 / 课件 / 勾选），再塞按钮会横向溢出 14px，
   所以窄屏由脚本把按钮挪到 body 上变成右下角悬浮（顶栏有 backdrop-filter，
   直接给它 position:fixed 会被顶栏接管定位，跑到屏幕外）。 */
.thbtn.fixed{position:fixed;right:18px;bottom:74px;z-index:70;height:40px;padding:0 14px;
box-shadow:0 6px 20px rgba(0,0,0,.28)}
@media(max-width:640px){.thbtn.fixed{right:14px;bottom:74px;height:36px;padding:0 12px}}
</style>"""

BODY_JS = """<script>(function(){
var KEY='py-theme-v1',ORDER=['auto','light','dark'];
var LABEL={auto:'跟随系统',light:'浅色',dark:'深色'};
var ICON={
auto:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="8"/><path d="M12 4a8 8 0 0 0 0 16z" fill="currentColor" stroke="none"/></svg>',
light:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.6v2.1M12 19.3v2.1M4.6 4.6l1.5 1.5M17.9 17.9l1.5 1.5M2.6 12h2.1M19.3 12h2.1M4.6 19.4l1.5-1.5M17.9 6.1l1.5-1.5"/></svg>',
dark:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M20.5 14.8A8.6 8.6 0 0 1 9.2 3.5a8.6 8.6 0 1 0 11.3 11.3z"/></svg>'};
var root=document.documentElement;
var q=window.matchMedia?window.matchMedia('(prefers-color-scheme:dark)'):null;
function mode(){var m=root.getAttribute('data-theme-mode');return ORDER.indexOf(m)<0?'auto':m}
function sync(m){
  var b=document.getElementById('thBtn');
  root.setAttribute('data-theme-mode',m);
  var d=root.getAttribute('data-theme')==='dark';
  var meta=document.querySelector('meta[name="theme-color"]');
  if(meta)meta.setAttribute('content',d?'#0f1620':'#1f5fa8');
  if(!b)return;
  b.title='主题：'+LABEL[m]+'　点一下切换（跟随系统 → 浅色 → 深色）';
  b.setAttribute('aria-label','主题：'+LABEL[m]+'，点击切换');
  var i=b.querySelector('.thi'),t=b.querySelector('.thlbl');
  if(i)i.innerHTML=ICON[m];if(t)t.textContent=LABEL[m];
}
function apply(m,save){
  var d=m==='dark'||(m==='auto'&&q&&q.matches);
  root.setAttribute('data-theme',d?'dark':'light');
  if(save){try{localStorage.setItem(KEY,m)}catch(e){}}
  sync(m);
}
function build(){
  var b=document.createElement('button');
  b.type='button';b.id='thBtn';b.className='thbtn';
  b.innerHTML='<span class="thi"></span><span class="thlbl"></span>';
  var host=document.querySelector('.top-in')||document.querySelector('.nav-in');
  var mq=window.matchMedia?window.matchMedia('(max-width:640px)'):null;
  if(host){host.appendChild(b)}else{document.body.appendChild(b)}
  function home(){
    var el=document.getElementById('thBtn');if(!el)return;
    var small=mq&&mq.matches;
    if(!host||small){
      if(el.parentElement!==document.body)document.body.appendChild(el);
      el.classList.add('fixed');
    }else{
      if(el.parentElement!==host)host.appendChild(el);
      el.classList.remove('fixed');
    }
  }
  home();
  if(mq&&mq.addEventListener)mq.addEventListener('change',home);
  window.__thHome=home;
  b.addEventListener('click',function(){apply(ORDER[(ORDER.indexOf(mode())+1)%3],true)});
  return b;
}
build();sync(mode());
if(q){var f=function(){if(mode()==='auto')apply('auto',false)};
  q.addEventListener?q.addEventListener('change',f):q.addListener(f)}
window.__theme={get mode(){return mode()},get dark(){return root.getAttribute('data-theme')==='dark'},
  set:function(m){apply(m,true)}};
})();</script>"""


def _strip_injected(html):
    html = re.sub(re.escape(HEAD_BEGIN) + r".*?" + re.escape(HEAD_END) + r"\n?",
                  "", html, flags=re.S)
    html = re.sub(re.escape(BODY_BEGIN) + r".*?" + re.escape(BODY_END) + r"\n?",
                  "", html, flags=re.S)
    return html


def _process_styles(html):
    def rep(m):
        body = m.group(2)
        if not body.strip():
            return m.group(0)
        return m.group(1) + css(body) + m.group(3)
    return re.sub(r"(<style[^>]*>)(.*?)(</style>)", rep, html, flags=re.S)


def inject(html):
    """给一个页面接上主题：派生深色样式 + head 脚本 + 顶栏按钮。"""
    if "<html" not in html or "</head>" not in html:
        return html
    html = _strip_injected(html)
    html = _process_styles(html)
    head = HEAD_BEGIN + "\n" + BASE_CSS + "\n" + HEAD_JS + "\n" + HEAD_END + "\n"
    m = re.search(r"<meta[^>]*charset[^>]*>", html, re.I)
    if m:
        html = html[:m.end()] + head + html[m.end():]
    else:
        html = html.replace("</head>", head + "</head>", 1)
    body = BODY_BEGIN + "\n" + BODY_JS + "\n" + BODY_END + "\n"
    idx = html.lower().rfind("</body>")
    if idx >= 0:
        html = html[:idx] + body + html[idx:]
    else:
        html = html + body
    return html


def write(path, text):
    if path.endswith(".css"):
        text = css(text)
    elif path.endswith(".html"):
        text = inject(text)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return text


def sweep(dirs=None, verbose=False):
    """批量处理目录里的 .html / .css（构建后兜底）。"""
    targets = dirs or [os.path.join(ROOT, p) for p in
                       ("web", "fluent", "python-course-ppt", ".", "android/www")]
    done, skipped = 0, 0
    seen = set()
    for base in targets:
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, files in os.walk(base):
            dirnames[:] = [d for d in dirnames
                           if d not in (".git", "node_modules", "www", "_cache",
                                        ".cache", "dist", "__pycache__")]
            for fn in files:
                if not fn.endswith((".html", ".css")):
                    continue
                fp = os.path.abspath(os.path.join(dirpath, fn))
                if fp in seen:
                    continue
                seen.add(fp)
                if "/android/" in fp.replace("\\", "/") and "/www/" not in fp.replace("\\", "/"):
                    skipped += 1
                    continue
                try:
                    src = open(fp, encoding="utf-8").read()
                except UnicodeDecodeError:
                    skipped += 1
                    continue
                if fn.endswith(".html") and "<html" not in src:
                    skipped += 1
                    continue
                out = css(src) if fn.endswith(".css") else inject(src)
                if out != src:
                    with open(fp, "w", encoding="utf-8", newline="") as f:
                        f.write(out)
                    done += 1
                    if verbose:
                        print("  theme:", os.path.relpath(fp, ROOT))
    return done, skipped


# ── 自检 ────────────────────────────────────────────────────────────────────
def _selftest():
    ok = True

    def chk(name, got, want):
        nonlocal ok
        if got != want:
            ok = False
            print(f"  FAIL {name}: {got!r} != {want!r}")

    chk("white->surface", _map_value("#fff", "surface"),
        hsl_to_hex(GREY_H, SURF_S * 0.86, SURF_RAMP[0][1]))
    chk("border brighter than card",
        rgb_to_hsl(*hex_to_rgb(_map_value("#e3e8ef", "divider")))[2]
        > rgb_to_hsl(*hex_to_rgb(_map_value("#fff", "surface")))[2], True)
    lifted = _map_value("#16232e", "ink")
    chk("ink lifted", rgb_to_hsl(*hex_to_rgb(lifted))[2] > 0.85, True)
    chk("ink lift keeps hex", lifted.startswith("#") and len(lifted) == 7, True)
    chk("accent kept", _map_value("#1f5fa8", "surface"), "#1f5fa8")
    chk("accent lifted", rgb_to_hsl(*hex_to_rgb(_map_value("#1f5fa8", "var")))[2] > 0.5, True)
    chk("var bg darkened", rgb_to_hsl(*hex_to_rgb(_map_value("#eaf1fb", "var")))[2] < 0.2, True)
    src = ":root{--bg:#f6f8fb;--text:#16232e}\n.a{background:#fff;color:#5f7183}\n" \
          "@media(max-width:600px){.b{background:#f2f5f9}}"
    once = css(src)
    twice = css(once)
    chk("idempotent", once, twice)
    chk("has mark", once.count(CSS_MARK), 1)
    chk("dark scoped", ':where(html[data-theme="dark"]) .a{' in once, True)
    chk("dark root", 'html[data-theme="dark"]{' in once, True)
    chk("media nested", ':where(html[data-theme="dark"]) .b{' in once, True)
    chk("light kept", '.a{background:#fff' in once, True)
    page = "<html><head><meta charset=\"utf-8\"><style>.a{background:#fff}</style>" \
           "</head><body><div class=\"top-in\"></div></body></html>"
    p1 = inject(page)
    p2 = inject(p1)
    chk("html idempotent", p1, p2)
    chk("head js once", p1.count("py-theme-v1"), 2)   # head 脚本 + body 脚本
    chk("button", "thBtn" in p1, True)
    print("selftest", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv):
    if "--selftest" in argv:
        return _selftest()
    verbose = "-v" in argv
    done, skipped = sweep(verbose=verbose)
    print(f"theme: 处理 {done} 个文件，跳过 {skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
