#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""为第一课生成讲解视频（无声 + 内置字幕，页面另配可选朗读）。

为什么不直接调文生视频模型：教学视频的命门是「字要看得清、节奏要跟讲义对齐」，
生成式视频在这两点上都不可控。这里改成 PIL 逐帧合成，文案来自讲义，
所以字幕、代码、高亮都能和课程正文严格对应，也不会有糊字。

渲染要点：
  - 1280×720 / 30fps，libx264 + yuv420p，CRF 26（保证文字边缘干净）；
  - 背景沿用站点那套「神经元」节点连线，视频和页面视觉是一家人；
  - 元素按 (延迟, 时长) 逐个入场，动效有 fade / up / left / pop；
    带 out 的元素到点自动淡出，用来做逐句切换的字幕条。

用法：
  python tools/make_lesson_video.py           # 生成 web/media/lesson01.mp4
  python tools/make_lesson_video.py --check   # 只检查产物
"""

import argparse
import json
import math
import os
import random
import subprocess
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 配音时间轴（可选）：有 make_lesson_audio 产出的音轨时，字幕起止和各幕时长
# 都由真实语音时长决定；没有就退回写死的节奏，视频照常生成（静音）。
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import make_lesson_audio as _NA
    NARR = _NA.load()
    AUDIO_WAV = _NA.OUT_WAV
except Exception:
    _NA, NARR, AUDIO_WAV = None, None, None

W, H, FPS = 1280, 720, 30
OUT_DIR = os.path.join(ROOT, "web", "media")
OUT_MP4 = os.path.join(OUT_DIR, "lesson01.mp4")
OUT_POSTER = os.path.join(OUT_DIR, "lesson01-poster.jpg")

F_REG = "C:/Windows/Fonts/msyh.ttc"
F_BOLD = "C:/Windows/Fonts/msyhbd.ttc"
F_MONO = "C:/Windows/Fonts/consola.ttf"

# ── 配色（深色底，与站点深色模式同源）──────────────────────────────
BG_TOP = (9, 15, 27)
BG_BOT = (21, 33, 55)
C_TXT = (222, 232, 244)
C_DIM = (136, 156, 180)
C_HI = (122, 194, 255)
C_OR = (255, 196, 107)
C_GR = (150, 226, 150)
C_RD = (255, 122, 122)
C_KEY = (255, 138, 170)
C_STR = (166, 231, 141)
C_NUM = (255, 196, 107)
C_CMT = (104, 126, 150)
C_CARD = (255, 255, 255, 14)
C_LINE = (255, 255, 255, 30)

# 六色神经元调色板（与 neuron.py 深色档一致）
PAL = [(117, 183, 255), (72, 222, 205), (186, 148, 255),
       (255, 170, 112), (255, 132, 178), (138, 226, 138)]

_FCACHE = {}


def font(path, size):
    key = (path, size)
    if key not in _FCACHE:
        _FCACHE[key] = ImageFont.truetype(path, size)
    return _FCACHE[key]


def ease(t):
    """easeOutCubic：起步快、收尾稳，最不容易出错的入场曲线。"""
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def ease_inout(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def clamp01(t):
    return max(0.0, min(1.0, t))


def layer(w, h):
    return Image.new("RGBA", (max(1, int(w)), max(1, int(h))), (0, 0, 0, 0))


def text_w(text, f):
    return ImageDraw.Draw(layer(8, 8)).textbbox((0, 0), text, font=f)[2]


def wrap(text, f, maxw):
    """按像素宽度折行。中英文混排统一按字符切——中文没有空格可依。"""
    tmp = ImageDraw.Draw(layer(8, 8))
    lines, cur = [], ""
    for ch in text:
        if ch == "\n":
            lines.append(cur)
            cur = ""
            continue
        if tmp.textbbox((0, 0), cur + ch, font=f)[2] > maxw and cur:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines or [""]


def text_block(text, f, color, maxw, lh=None):
    lines = wrap(text, f, maxw)
    lh = lh or int(f.size * 1.55)
    im = layer(maxw, len(lines) * lh + 6)
    d = ImageDraw.Draw(im)
    y = 0
    for ln in lines:
        d.text((0, y), ln, font=f, fill=color)
        y += lh
    return im


def card(w, h, radius=18, fill=C_CARD, outline=C_LINE):
    im = layer(w, h)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=fill,
                        outline=outline, width=1)
    return im


def hline(w, h=3, col=C_HI, alpha=185):
    """横向渐变线（两端淡、中间实），标题下的高亮条。"""
    im = layer(max(1, int(w)), h)
    d = ImageDraw.Draw(im)
    for x in range(max(1, int(w))):
        p = x / max(1.0, w - 1)
        a = int(alpha * (1 - abs(p - .5) * 2) ** .6)
        d.line([(x, 0), (x, h - 1)], fill=col + (a,))
    return im


def dot_bullet(size=13, col=C_HI):
    im = layer(size + 10, size + 10)
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, size, size], fill=col + (235,))
    return im


def check_bullet(size=22, col=C_GR, tick=1.0):
    """自检清单的方框 + 打勾，tick 控制勾的绘制进度。"""
    im = layer(size + 12, size + 12)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([1, 1, size, size], radius=6,
                        fill=(255, 255, 255, 14), outline=col + (190,), width=2)
    if tick > 0:
        pts = [(7, size // 2 + 2), (size // 2 - 1, size - 6), (size - 3, 6)]
        n = max(2, int(len(pts) * min(1.0, tick)))
        if n >= len(pts):
            d.line(pts, fill=col + (245,), width=3, joint="curve")
        else:
            d.line(pts[:n], fill=col + (200,), width=3, joint="curve")
    return im


def window_frame(d, box, title, f_title, accent=C_HI):
    """窗口外框：标题栏 + 三个交通灯圆点 + 标题文字。"""
    x0, y0, x1, y1 = box
    d.rounded_rectangle([x0, y0, x1, y1], radius=14,
                        fill=(12, 20, 34, 238), outline=(255, 255, 255, 44), width=1)
    d.line([(x0 + 14, y0 + 44), (x1 - 14, y0 + 44)], fill=(255, 255, 255, 36))
    cx = x0 + 24
    for col in ((255, 95, 86), (255, 189, 46), (39, 201, 63)):
        d.ellipse([cx, y0 + 16, cx + 11, y0 + 27], fill=col + (210,))
        cx += 20
    d.text((x0 + 100, y0 + 11), title, font=f_title, fill=accent + (235,))


def foot(text):
    """底部字幕条（mono 与中文自动选字体）。"""
    ascii_only = all(ord(c) < 128 for c in text)
    f = font(F_MONO, 25) if ascii_only else font(F_REG, 27)
    bw = min(W - 120, text_w(text, f) + 52)
    im = layer(bw, 46)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, bw - 1, 45], radius=12,
                        fill=(7, 13, 24, 216), outline=(255, 255, 255, 34))
    d.text((26, 11), text, font=f, fill=C_TXT)
    return im


# ── 配音驱动的字幕 / 幕长 ───────────────────────────────────────
def _tl(idx):
    """该幕每句的 (开始, 时长)；无配音时返回 None。"""
    if NARR and idx < len(NARR["scenes"]):
        return [(x["t"], x["d"]) for x in NARR["scenes"][idx]["subs"]]
    return None


def sub_els(idx, y=646, base=.25, step=1.7, with_bar=True):
    """按配音时间轴铺字幕条：说到哪句亮哪句，说完淡出。

    with_bar=False 用于片头——那里已有大标题和副标题，只念不重复出字幕条。
    """
    texts = _NA.sub_texts(idx) if _NA else []
    tl = _tl(idx)
    els = []
    if not with_bar:
        return els
    for i, s in enumerate(texts):
        st, du = (tl[i][0], tl[i][1]) if tl and i < len(tl) else (base + i * step, step)
        out = None if i == len(texts) - 1 else st + du + .12
        els.append(el(foot(s), 0, y, st, .45, out=out))
    return els


def scene_dur(idx, base):
    """幕长取「动画需要的时间」和「念完需要的时间」里更大的那个。"""
    if NARR and idx < len(NARR["scenes"]):
        return max(base, NARR["scenes"][idx]["dur"])
    return base


# ── 背景：神经元 ────────────────────────────────────────────────
def make_bg():
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        p = y / (H - 1)
        d.line([(0, y), (W, y)],
               fill=(int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * p),
                     int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * p),
                     int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * p)))
    g = Image.new("RGB", (W, H))
    gd = ImageDraw.Draw(g)
    gd.ellipse([-280, -320, 640, 540], fill=(24, 56, 102))
    gd.ellipse([700, 360, 1440, 920], fill=(18, 38, 74))
    return Image.blend(im, g, 0.38).convert("RGBA")


def seed_nodes(n):
    rnd = random.Random(20261029)
    return [{"x": rnd.random() * W, "y": rnd.random() * H,
             "vx": (rnd.random() - .5) * .20, "vy": (rnd.random() - .5) * .20,
             "r": rnd.random() * 1.2 + 1.3, "c": int(rnd.random() * len(PAL))}
            for _ in range(n)]


def nodes_at(nodes, t):
    """匀速漂移 + 环绕。速度压得很慢，别抢正文注意力。"""
    return [{"x": (a["x"] + a["vx"] * t * 30) % (W + 48) - 24,
             "y": (a["y"] + a["vy"] * t * 30) % (H + 48) - 24,
             "r": a["r"], "c": a["c"]} for a in nodes]


def draw_neurons(d, nodes):
    link, l2 = 130.0, 130.0 * 130.0
    for i, a in enumerate(nodes):
        for j in range(i + 1, len(nodes)):
            b = nodes[j]
            dx, dy = a["x"] - b["x"], a["y"] - b["y"]
            d2 = dx * dx + dy * dy
            if d2 > l2:
                continue
            k = (1 - math.sqrt(d2) / link) * .34
            ca, cb = PAL[a["c"]], PAL[b["c"]]
            d.line([(a["x"], a["y"]), (b["x"], b["y"])],
                   fill=((ca[0] + cb[0]) // 2, (ca[1] + cb[1]) // 2,
                          (ca[2] + cb[2]) // 2, int(k * 255)))
    for a in nodes:
        c = PAL[a["c"]]
        r = a["r"]
        d.ellipse([a["x"] - r, a["y"] - r, a["x"] + r, a["y"] + r],
                   fill=c + (165,))


# ── 元素系统 ────────────────────────────────────────────────────
def el(img, x, y, delay=0.0, dur=0.5, kind="fade", out=None):
    """kind: fade 淡入 / up 上滑 / left 左侧滑入 / pop 缩放弹出；out 为淡出时刻。"""
    return {"img": img, "x": x, "y": y, "delay": delay, "dur": dur,
            "kind": kind, "out": out}


def place(canvas, e, lt):
    """把一个元素按当前局部时间合成到画布。"""
    p = (lt - e["delay"]) / e["dur"]
    if p <= 0:
        return
    a = ease(p)
    if e["out"] is not None:
        a = a * (1 - clamp01((lt - e["out"]) / .35))
        if a <= 0.01:
            return
    img, x, y = e["img"], e["x"], e["y"]
    if e["kind"] == "up":
        y += int((1 - a) * 26)
    elif e["kind"] == "left":
        x -= int((1 - a) * 42)
    elif e["kind"] == "pop":
        s = 0.93 + 0.07 * a
        w, h = max(1, int(img.width * s)), max(1, int(img.height * s))
        img = img.resize((w, h), ImageDraw.Image.LANCZOS if hasattr(ImageDraw, "Image") else Image.LANCZOS)
        x += (e["img"].width - w) // 2
        y += (e["img"].height - h) // 2
    if a >= 0.999:
        canvas.alpha_composite(img, (x, y))
        return
    m = img.getchannel("A").point(lambda v: int(v * a))
    tmp = img.copy()
    tmp.putalpha(m)
    canvas.alpha_composite(tmp, (x, y))


def head(num, title):
    """场景标题：大号序号 + 标题 + 分隔线。"""
    return [
        el(text_block(num, font(F_BOLD, 58), C_HI, 150), 78, 124, .0, .5, "left"),
        el(text_block(title, font(F_BOLD, 44), C_TXT, 900), 214, 136, .1, .5, "left"),
        el(hline(430), 80, 202, .3, .7),
    ]


def seq(*parts):
    out = []
    for p in parts:
        out.extend(p)
    return out


def seg(text, col=C_TXT):
    """一段同色字符。换行符传默认色即可，它本身不显示。"""
    return [(c, col) for c in text]


def type_chars(d, chars, f, origin, nvis, lh):
    """逐字符画代码，返回光标应处的 (x, y)。
    Consolas 没有中文字形，CJK 字符逐个 fallback 到雅黑，否则注释变方块。"""
    f_cjk = font(F_REG, f.size + 1)
    x0, y0 = origin
    x, y = x0, y0
    n = int(nvis)
    cnt = 0
    for c, col in chars:
        if cnt >= n:
            break
        if c == "\n":
            x = x0
            y += lh
            cnt += 1
            continue
        fc = f_cjk if ord(c) >= 0x2E80 else f
        d.text((x, y), c, font=fc, fill=col)
        x += fc.getlength(c)
        cnt += 1
    return x, y


def cursor(d, x, y, lt, col=C_HI):
    if int(lt * 3.2) % 2 == 0:
        d.rectangle([x + 2, y + 6, x + 12, y + 38], fill=col + (215,))


# ══════════════ 第一幕：片头 ══════════════
def scene_intro():
    els = [
        el(text_block("入门 · 第 1 课", font(F_BOLD, 27), C_HI, 520), 130, 244, .0, .6, "up"),
        el(hline(260), 132, 304, .25, .8),
        el(text_block("装好 Python 与 VS Code", font(F_BOLD, 60), C_TXT, 1040), 128, 314, .25, .7, "up"),
        el(text_block("90 分钟 · 先把三个角色分清：编辑器、终端、解释器",
                      font(F_REG, 29), C_DIM, 1040), 130, 410, .7, .6, "up"),
    ]
    return scene_dur(0, 4.6), els, None


# ══════════════ 第二幕：解释器 ══════════════
def scene_interp():
    els = head("01", "Python 解释器")
    pts = [
        ("你写的 hello.py —— 只是一张菜谱", C_TXT, C_OR),
        ("python 解释器 —— 照着菜谱做菜的厨师", C_TXT, C_OR),
        ("没装解释器，代码就只是一堆普通文本", C_HI, C_HI),
    ]
    y = 238
    for i, (p, tc, dc) in enumerate(pts):
        d0 = .45 + i * .6
        els.append(el(dot_bullet(13, dc), 84, y + 9, d0, .35))
        els.append(el(text_block(p, font(F_REG, 30), tc, 830), 118, y, d0, .5, "left"))
        y += 56

    boxes = [(96, 436, 346, 556), (376, 436, 626, 556), (656, 436, 906, 556)]
    labels = ["hello.py", "python", "Hello, Python!"]
    colors = [C_OR, C_HI, C_GR]
    for i, ((x0, y0, x1, y1), lab, col) in enumerate(zip(boxes, labels, colors)):
        w, h = x1 - x0, y1 - y0
        c = layer(w, h)
        cd = ImageDraw.Draw(c)
        cd.rounded_rectangle([0, 0, w - 1, h - 1], radius=14,
                             fill=col + (22,), outline=col + (155,), width=2)
        tl = text_block(lab, font(F_BOLD, 29), col, w - 40)
        c.alpha_composite(tl, ((w - tl.width) // 2, (h - tl.height) // 2))
        els.append(el(c, x0, y0, 2.0 + i * .85, .5, "pop"))

    def arrows(img, d, lt):
        for i in range(len(boxes) - 1):
            x0 = boxes[i][2] + 14
            x1 = boxes[i + 1][0] - 14
            yy = (boxes[i][1] + boxes[i][3]) // 2
            col = colors[i + 1]
            p = clamp01((lt - (2.9 + i * .85)) / .4)
            if p <= 0:
                continue
            xe = x0 + (x1 - x0) * ease(p)
            d.line([(x0, yy), (xe, yy)], fill=col + (205,), width=3)
            if p > .8:
                a = int(255 * min(1.0, (p - .8) / .2))
                d.polygon([(x1, yy), (x1 - 10, yy - 7), (x1 - 10, yy + 7)],
                         fill=col + (a,))

    els += sub_els(1, y=640, base=.3, step=1.7)
    return scene_dur(1, 11.4), els, arrows


# ══════════════ 第三幕：终端 ══════════════
TERM_CHARS = seq(
    seg("PS C:\\py-course> ", (110, 138, 168)),
    seg("python --version", C_TXT), seg("\n"),
    seg("Python 3.12.4", C_GR), seg("\n"),
    seg("PS C:\\py-course> ", (110, 138, 168)),
    seg("python hello.py", C_TXT), seg("\n"),
    seg("Hello, Python!", C_HI),
)


def scene_term():
    els = head("02", "终端 / 命令行")
    pts = [
        ("终端是你和解释器说话的那个窗口", C_TXT, C_OR),
        ("python hello.py —— 让厨师照这份菜谱做一遍", C_TXT, C_OR),
        ("报错也在这里看：它话多，但不咬人", C_GR, C_GR),
    ]
    y = 238
    for i, (p, tc, dc) in enumerate(pts):
        d0 = .4 + i * .6
        els.append(el(dot_bullet(13, dc), 84, y + 9, d0, .35))
        els.append(el(text_block(p, font(F_REG, 30), tc, 830), 118, y, d0, .5, "left"))
        y += 56

    box = (110, 402, 950, 638)
    f_m = font(F_MONO, 29)
    f_t = font(F_BOLD, 23)

    def draw(img, d, lt):
        window_frame(d, box, "PowerShell", f_t)
        p = clamp01((lt - .5) / 4.4)
        nvis = len(TERM_CHARS) * ease_inout(p)
        cx, cy = type_chars(d, TERM_CHARS, f_m, (box[0] + 28, box[1] + 58), nvis, 40)
        if p < 1:
            cursor(d, cx, cy, lt)

    els += sub_els(2, y=646, base=.25, step=1.7)
    return scene_dur(2, 11.2), els, draw


# ══════════════ 第四幕：VS Code ══════════════
VS_CHARS = seq(
    seg("# 我的第一个 Python 程序\n", C_CMT),
    seg("name", C_TXT), seg(" = ", C_DIM), seg('"Python"', C_STR), seg("\n"),
    seg("print", C_KEY), seg("(", C_DIM),
    seg('f"Hello, ', C_STR), seg("{name}", C_OR), seg('!"', C_STR),
    seg(")", C_DIM),
)


def scene_vscode():
    els = head("03", "VS Code + Python 扩展")
    pts = [
        ("编辑器是写字板：高亮、缩进、文件树", C_TXT, C_OR),
        ("Python 扩展补上：智能提示、红波浪线、▶ 运行", C_TXT, C_OR),
        ("编辑器负责写，解释器负责跑", C_HI, C_HI),
    ]
    y = 238
    for i, (p, tc, dc) in enumerate(pts):
        d0 = .4 + i * .6
        els.append(el(dot_bullet(13, dc), 84, y + 9, d0, .35))
        els.append(el(text_block(p, font(F_REG, 30), tc, 830), 118, y, d0, .5, "left"))
        y += 56

    box = (110, 420, 950, 618)
    f_m = font(F_MONO, 29)
    f_t = font(F_BOLD, 23)

    def draw(img, d, lt):
        window_frame(d, box, "hello.py — VS Code", f_t)
        d.rectangle([box[0] + 1, box[1] + 45, box[0] + 50, box[3] - 1],
                    fill=(255, 255, 255, 10))
        for i, ln in enumerate(["1", "2", "3"]):
            d.text((box[0] + 18, box[1] + 66 + i * 42), ln,
                   font=font(F_MONO, 23), fill=(94, 114, 138))
        p = clamp01((lt - .45) / 3.2)
        nvis = len(VS_CHARS) * ease_inout(p)
        cx, cy = type_chars(d, VS_CHARS, f_m, (box[0] + 66, box[1] + 66), nvis, 42)
        if p < 1:
            cursor(d, cx, cy, lt)
        # ▶ 运行按钮：脉冲提示
        cx2, cy2 = box[2] - 58, box[1] + 26
        pulse = .5 + .5 * math.sin(lt * 3.2)
        rr = 16 + int(pulse * 4)
        d.ellipse([cx2 - rr, cy2 - rr, cx2 + rr, cy2 + rr],
                  fill=C_HI + (int(34 + pulse * 60),))
        d.polygon([(cx2 - 5, cy2 - 9), (cx2 - 5, cy2 + 9), (cx2 + 9, cy2)],
                  fill=C_GR + (240,))

    els += sub_els(3, y=646, base=.25, step=1.7)
    return scene_dur(3, 11.2), els, draw


# ══════════════ 第五幕：跟着敲 ══════════════════════════════════
ERR_CHARS = seq(seg('print("Hello, Python!"', C_TXT))


def scene_practice():
    els = head("04", "跟着敲：hello.py")
    f_m = font(F_MONO, 29)
    f_t = font(F_BOLD, 23)
    box = (110, 242, 950, 442)
    obox = (110, 466, 950, 588)

    def draw(img, d, lt):
        broken = lt > 7.2
        chars = ERR_CHARS if broken else VS_CHARS
        window_frame(d, box, "hello.py", f_t)
        d.rectangle([box[0] + 1, box[1] + 45, box[0] + 50, box[3] - 1],
                    fill=(255, 255, 255, 10))
        for i, ln in enumerate(["1", "2", "3"]):
            d.text((box[0] + 18, box[1] + 62 + i * 42), ln,
                   font=font(F_MONO, 23), fill=(94, 114, 138))
        p = 1.0 if broken else clamp01((lt - .3) / 3.0)
        cx, cy = type_chars(d, chars, f_m, (box[0] + 66, box[1] + 62),
                              len(chars) * ease_inout(p), 42)
        if not broken and p < 1:
            cursor(d, cx, cy, lt)

        # 输出面板：成功后绿字，写错后红字
        if lt > 3.6 and not broken:
            q = ease(clamp01((lt - 3.6) / .6))
            w, h = obox[2] - obox[0], obox[3] - obox[1]
            sub = layer(w, h)
            sd = ImageDraw.Draw(sub)
            window_frame(sd, (0, 0, w, h), "输出 — 终端", f_t)
            sd.text((30, 64), "Hello, Python!", font=font(F_MONO, 29), fill=C_GR)
            sub.putalpha(sub.getchannel("A").point(lambda v: int(v * q)))
            img.alpha_composite(sub, (obox[0], obox[1] + int((1 - q) * 20)))
        elif broken:
            q = ease(clamp01((lt - 7.2) / .6))
            w, h = obox[2] - obox[0], obox[3] - obox[1]
            sub = layer(w, h)
            sd = ImageDraw.Draw(sub)
            window_frame(sd, (0, 0, w, h), "输出 — 终端", f_t)
            sd.text((30, 56), "File \"hello.py\", line 3",
                    font=font(F_MONO, 24), fill=C_DIM)
            sd.text((30, 72), "SyntaxError: '(' was never closed",
                    font=font(F_MONO, 26), fill=C_RD)
            sub.putalpha(sub.getchannel("A").point(lambda v: int(v * q)))
            img.alpha_composite(sub, (obox[0], obox[1] + int((1 - q) * 20)))

    els += sub_els(4, y=646, base=.25, step=2.5)
    return scene_dur(4, 13.0), els, draw


# ══════════════ 第六幕：小结 ══════════════
def scene_summary():
    els = head("05", "本节自检")
    items = [
        ("终端里敲 python --version，能看到版本号", C_GR),
        ("能自己新建 .py 文件，并把它跑出结果", C_GR),
        ("故意写错时，看得懂报错最后一行在说什么", C_OR),
    ]
    y = 244
    for i, (txt, col) in enumerate(items):
        d0 = .5 + i * .8
        els.append(el(check_bullet(22, col, 1.0), 84, y + 2, d0, .5, "pop"))
        els.append(el(text_block(txt, font(F_REG, 31), C_TXT, 900), 130, y, d0, .55, "left"))
        y += 68

    nxt = card(600, 96, radius=16)
    nd = ImageDraw.Draw(nxt)
    t1 = text_block("下一课", font(F_BOLD, 24), C_HI, 540)
    t2 = text_block("变量 —— 一个贴了标签的盒子", font(F_BOLD, 32), C_TXT, 540)
    nxt.alpha_composite(t1, (30, 20))
    nxt.alpha_composite(t2, (30, 50))
    els.append(el(nxt, 110, 504, 3.6, .7, "up"))

    els += sub_els(5, y=646, base=.3, step=2.0)
    return scene_dur(5, 11.5), els, None


# 各幕动画的「设计时长」：配音更长时按比例把动画放慢，避免画面演完干等
BASE_DUR = [4.6, 11.4, 11.2, 11.2, 13.0, 11.5]


def build_scenes():
    sc = [scene_intro(), scene_interp(), scene_term(),
          scene_vscode(), scene_practice(), scene_summary()]
    out = []
    for i, (dur, els, cus) in enumerate(sc):
        out.append((dur, els, cus, dur / BASE_DUR[i]))
    return out


# ── 讲解员：DeepSeek 官方 Q 版鲸鱼娘动画（dsh-pet 桌宠素材）──────
# 素材由 tools/make_pet_assets.py 从 DSH 桌宠插件提取：
#   · standalone 帧序列（RGBA 透明 webp，11 个动作）
#   · 插件本体黑底 webm → 亮度键抠图（6 个动作）
# 每个动作 241 帧 / 10s @24fps，非循环；pet_meta.json 存每帧脸框
# （肤色连通域逐帧跟踪）与嘴锚点。对齐用「动作第 1 帧的脸框中心」，
# 动作内部帧不校正——保住官方动画里跳跃/移动的表现力。
PET_DIR = os.path.join(ROOT, "tools", "assets", "pet")
CHAR_H = 330            # 角色显示高度（角色本体，Q 版显小所以比立绘时代大）
# 脸在帧坐标系里的屏幕锚点（沿用立绘时代的视觉位置）
FACE_ANCHOR = (1105.0, 492.0)
FADE = 0.5                   # 动作切换的交叉淡入时长（30fps = 15 帧）
PREP = 0.22                  # 切换前的「预备」：先沉一下再起身
_ROI = (940, 320, 1280, 680)  # 角色活动范围，交叉溶解只在这块做像素运算
_PET_META = None
_PET_CLIP = {}               # 动作名 → 缩放后整帧缓存（仅当前用到的动作）

# 每幕的姿势时间表（幕内真实秒 → 官方动画动作）。切换点落在两句台词
# 之间的留白，时间取自 make_lesson_audio.py --check 的句子起止。
# wave=元气挥手 idle=待机呼吸 code=写代码 type=忙碌点按 happy=开心跃动
# think=思考冒泡 shy=害羞惊讶 angry=傲娇生气 sigh=垂头叹气 party=雀跃庆祝
# bow=女仆屈膝礼仪（告别鞠躬）
POSE_CUES = {
    0: [(0.0, "wave")],                                        # 片头打招呼
    1: [(0.0, "idle"), (4.65, "code"), (8.35, "happy")],       # 解释器 → 该动手了
    2: [(0.0, "type"), (4.85, "happy"), (9.75, "code")],       # 终端 → 验证/进目录
    3: [(0.0, "idle"), (5.00, "code"), (8.95, "sigh")],        # VS Code → 红波浪线别怕
    4: [(0.0, "think"), (4.35, "shy"), (9.05, "angry")],       # 跟敲 → 强调 → 报错
    5: [(0.0, "happy"), (4.05, "party"), (8.35, "bow")],       # 小结 → 告别屈膝礼
}


def pet_meta():
    global _PET_META
    if _PET_META is None:
        with open(os.path.join(PET_DIR, "pet_meta.json"), encoding="utf-8") as f:
            _PET_META = json.load(f)
    return _PET_META


def pet_clip(name):
    """某动作的渲染常量：缩放系数、对齐偏移、脸框表。懒加载缓存。"""
    if name not in _PET_CLIP:
        m = pet_meta()[name]
        im0 = Image.open(os.path.join(PET_DIR, m["dir"], "f_0000.webp")).convert("RGBA")
        bb = im0.getchannel("A").getbbox()
        sc = CHAR_H / float(bb[3] - bb[1])
        fx = (m["face0"][0] + m["face0"][2]) / 2.0
        fy = (m["face0"][1] + m["face0"][3]) / 2.0
        # 动作第 1 帧的脸框中心对齐到 FACE_ANCHOR：换动作时角色不跳，
        # 动作内部的跳跃/移动全部保留（这是官方动画的表现力所在）
        _PET_CLIP[name] = {"dir": os.path.join(PET_DIR, m["dir"]),
                           "n": m["frames"], "sc": sc, "boxes": m["boxes"],
                           "mrel": m["mouth_rel"],
                           "off": (FACE_ANCHOR[0] - fx * sc,
                                   FACE_ANCHOR[1] - fy * sc)}
    return _PET_CLIP[name]


def pet_frame(name, idx, dx=0.0, dy=0.0):
    """取动作第 idx 帧解码缩放，返回 (图, 左上角屏幕坐标, 嘴屏幕坐标)。"""
    c = pet_clip(name)
    idx = max(0, min(idx, c["n"] - 1))
    im = Image.open(os.path.join(c["dir"], "f_%04d.webp" % idx)).convert("RGBA")
    if abs(c["sc"] - 1.0) > 0.004:
        im = im.resize((max(1, round(im.width * c["sc"])),
                        max(1, round(im.height * c["sc"]))), Image.LANCZOS)
    bb = c["boxes"][idx]
    mx = bb[0] + c["mrel"][0] * (bb[2] - bb[0])
    my = bb[1] + c["mrel"][1] * (bb[3] - bb[1])
    pos = (int(round(c["off"][0] + dx)), int(round(c["off"][1] + dy)))
    mpos = (mx * c["sc"] + c["off"][0] + dx, my * c["sc"] + c["off"][1] + dy)
    return im, pos, mpos


_GCUES = []          # 全局时间轴：[(全局秒, 姿势名)]，跨幕展开


def build_global_cues(scenes):
    """把分幕的 POSE_CUES 展开成一条全局时间轴。

    必须全局：按幕查表时新幕首帧的 prev 是 None，幕与幕之间的 5 个边界
    就还是硬切（只有幕内 cue 切换有过渡）。展开后边界自动被覆盖——
    上一幕最后的姿势淡出 → 新幕第一个姿势淡入。
    """
    global _GCUES
    acc, out = 0.0, []
    for si, (dur, _, _, _) in enumerate(scenes):
        for t0, p in (POSE_CUES.get(si) or POSE_CUES[0]):
            out.append((acc + t0, p))
        acc += dur
    _GCUES = out
    return out


def pose_at(t):
    """全局秒 t 处该用哪个姿势、上一个姿势是什么、各自已播多久。"""
    if not _GCUES:
        build_global_cues(build_scenes())
    name, prev, since = _GCUES[0][1], None, t - _GCUES[0][0]
    prev_el = 0.0
    for i, (t0, p) in enumerate(_GCUES):
        if t >= t0:
            prev_el = t - _GCUES[i - 1][0] if i > 0 else 0.0
            name, since = p, t - t0
            prev = _GCUES[i - 1][1] if i > 0 else None
    return name, prev, since, prev_el


def faded(im, a):
    """给 RGBA 图乘一个全局 alpha（复合位图的 out = src + dst(1-alpha)，
    要半透只能改 src 的 alpha 通道）。LUT 比逐像素 python 回调快得多。"""
    if a >= .995:
        return im
    if a <= .005:
        return None
    out = im.copy()
    out.putalpha(im.getchannel("A").point([int(v * a) for v in range(256)]))
    return out


def next_cue(t):
    """t 之后下一个切换时刻（用于预备动作），没有就返回 None。"""
    for t0, _ in _GCUES:
        if t0 > t:
            return t0
    return None


def crossfade(canvas, A, posA, B, posB, k):
    """真正的交叉溶解 out = A*(1-k) + B*k。

    PIL 的 alpha_composite 是 src-over：把两张半透明图一前一后叠上去，重叠区
    （头/身体，两张都有）的 alpha 会变成 k+(1-k)(1-k)——k=0.5 时只剩 0.75，
    头部半透明、背景神经元线条透出来，看着就是在闪。正确做法是先合到一张
    临时层：A 实心打底、B 按 k 淡入（重叠区恒不透明），再把「只有 A 有的
    那一块」（旧手臂）单独按 k 淡出。
    """
    rx0, ry0, rx1, ry1 = _ROI
    w, h = rx1 - rx0, ry1 - ry0
    la = layer(w, h)
    la.alpha_composite(A, (posA[0] - rx0, posA[1] - ry0))
    lb = layer(w, h)
    lb.alpha_composite(B, (posB[0] - rx0, posB[1] - ry0))
    only = ImageChops.subtract(la.getchannel("A"), lb.getchannel("A"))
    fb = faded(lb, k)
    if fb is not None:
        la.alpha_composite(fb, (0, 0))
    la.putalpha(ImageChops.subtract(
        la.getchannel("A"), only.point([int(v * k) for v in range(256)])))
    canvas.alpha_composite(la, (rx0, ry0))


def draw_char(canvas, t, mouth, dx=0):
    name, prev, since, prev_el = pose_at(t)
    fps = 24.0
    hop = -abs(math.sin(t * 3.2)) * 2.5 * mouth     # 说话时低频小幅起伏
    nxt = next_cue(t)
    if nxt is not None:
        d = nxt - t
        if d < PREP:                                # 预备：先沉一下再换动作
            hop += (1 - d / PREP) * 3.0
    if prev is not None and since < FADE:
        k = ease_inout(since / FADE)
        # 旧动作帧停在切换瞬间；新动作从 0 帧开始播
        A, pa, _ = pet_frame(prev, int(prev_el * fps), dx, hop + 6 * k)
        B, pb, mpos = pet_frame(name, int(since * fps), dx, hop - 9 * (1 - k))
        crossfade(canvas, A, pa, B, pb, k)
        mpx, mpy = mpos
    else:
        B, pb, mpos = pet_frame(name, int(since * fps), dx, hop)
        canvas.alpha_composite(B, pb)
        mpx, mpy = mpos
    # 口型：官方动画没有说话口型，按脸框宽度自适应画一个小开合贴片
    # （Q 版嘴原画只有 ~3px，贴片略放大到脸宽 15%，配合音波示意说话）
    c = pet_clip(name)
    idx = max(0, min(int(since * fps), c["n"] - 1))
    bb = c["boxes"][idx]
    face_w = max(20.0, (bb[2] - bb[0]) * c["sc"])
    mw = face_w * 0.15
    oh = 0.7 + mouth * 3.2
    d2 = ImageDraw.Draw(canvas)
    if mouth > .08:
        top = mpy - 1.0
        d2.ellipse([mpx - mw / 2, top, mpx + mw / 2, top + 2 * oh],
                   fill=(104, 40, 58))
        if mouth > .32:
            d2.ellipse([mpx - mw * .27, top + oh * .4,
                        mpx + mw * .27, top + oh * 1.3], fill=(222, 118, 128))
    # 说话音波：嘴右侧两条弧，开度越大越亮
    if mouth > .1:
        hx, hy = mpx + face_w * 0.42, mpy - face_w * 0.30
        for i in range(2):
            r = 5 + i * 5
            col = (int(100 + 70 * mouth + i * 12), 195, 255)
            d2.arc([hx + i * 5, hy - r, hx + i * 5 + 2 * r, hy + r],
                   start=-52, end=52, fill=col, width=2)


def load_env(path, total):
    """从音轨算出每帧的音量包络（0..1），拿来驱动嘴的开合。"""
    if not path or not os.path.exists(path):
        return None
    try:
        import array
        import wave
        with wave.open(path, "rb") as wf:
            sr = wf.getframerate()
            pcm = array.array("h")
            pcm.frombytes(wf.readframes(wf.getnframes()))
    except Exception:
        return None
    if not pcm:
        return None
    win = int(sr * 0.055)
    raw = []
    for f in range(int(total * FPS) + 2):
        c = int(f / FPS * sr)
        a, b = max(0, c - win), min(len(pcm), c + win)
        if b <= a:
            raw.append(0.0)
            continue
        step = 3
        s = 0
        for i in range(a, b, step):
            v = pcm[i]
            s += v * v
        raw.append(math.sqrt(s / max(1.0, (b - a) / step)))
    mx = max(raw) or 1.0
    # 55% 峰值算「满嘴」，再滑动平均抹掉逐帧抖动
    env = [min(1.0, v / (mx * 0.55)) for v in raw]
    return [sum(env[max(0, i - 1):i + 2]) / len(env[max(0, i - 1):i + 2])
            for i in range(len(env))]


# ── HUD ─────────────────────────────────────────────────────────
def pbar(d, g):
    """底部进度条（g = 全局进度 0..1）。用不透明色，不依赖 blend 模式。"""
    d.rectangle([0, H - 5, W, H - 1], fill=(38, 50, 70))
    d.rectangle([0, H - 5, max(0, int(W * g)), H - 1], fill=C_HI)


def chapter_badge(text):
    """右上角常驻章节标签。"""
    f = font(F_BOLD, 26)
    tw = text_w(text, f)
    bw = tw + 36
    im = layer(bw, 40)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, bw - 1, 39], radius=10,
                        fill=(122, 194, 255, 30), outline=(122, 194, 255, 85))
    d.text((18, 8), text, font=f, fill=C_HI)
    return im


# ── 渲染 ────────────────────────────────────────────────────────
def render():
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR, exist_ok=True)
    scenes = build_scenes()
    build_global_cues(scenes)
    total = sum(d for d, _, _, _ in scenes)
    nframes = int(round(total * FPS))
    print("时长 %.1fs / %d 帧 / %d 幕" % (total, nframes, len(scenes)))

    bg = make_bg()
    nodes = seed_nodes(58)
    env = load_env(AUDIO_WAV, total) if NARR else None
    print("嘴型驱动：" + ("语音音量包络 %d 帧" % len(env) if env else "无（静音则闭嘴）"))
    lay_n = layer(W, H)
    lay_c = layer(W, H)
    dn = ImageDraw.Draw(lay_n)
    dc = ImageDraw.Draw(lay_c)

    badges = ["入门 · 第 1 课", "解释器", "终端", "VS Code", "跟着敲", "自检"]

    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        print("缺少 imageio-ffmpeg，请先 pip install imageio-ffmpeg")
        return 1

    cmd = [exe, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-"]
    if NARR:
        cmd += ["-i", AUDIO_WAV]
    cmd += ["-map", "0:v:0", "-c:v", "libx264", "-preset", "medium", "-crf", "26",
            "-pix_fmt", "yuv420p"]
    if NARR:
        # 音轨长度由时间轴算出，画面只会更长（幕长取 max），所以不会截断语音
        cmd += ["-map", "1:a:0", "-c:a", "aac", "-b:a", "96k", "-shortest"]
    else:
        cmd += ["-an"]
    cmd += ["-movflags", "+faststart", OUT_MP4]
    print("配音：" + (("%s · %.1fs" % (NARR["voice"], NARR["total"])) if NARR
                      else "无（静音，跑 make_lesson_audio.py 可加旁白）"))
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    poster = None
    try:
        for f in range(nframes):
            t = f / FPS
            acc = 0.0
            for si, (dur, els, cus, scale) in enumerate(scenes):
                if t < acc + dur or si == len(scenes) - 1:
                    lt = (t - acc) / scale      # 动画时间按配音拉长的比例放慢
                    bidx = si
                    break
                acc += dur
            canvas = bg.copy()
            dn.rectangle([0, 0, W, H], fill=(0, 0, 0, 0))
            draw_neurons(dn, nodes_at(nodes, t))
            canvas.alpha_composite(lay_n)

            els = scenes[bidx][1]
            for e in els:
                place(canvas, e, lt)
            cus = scenes[bidx][2]
            if cus:
                dc.rectangle([0, 0, W, H], fill=(0, 0, 0, 0))
                cus(lay_c, dc, lt)
                canvas.alpha_composite(lay_c)

            bimg = chapter_badge(badges[bidx])
            canvas.alpha_composite(bimg, (W - bimg.width - 46, 30))

            # 讲解员：开场 0.9 秒从右侧滑入，之后常驻右下角
            mouth = env[f] if env and f < len(env) else 0.0
            slide = 0 if t > .9 else int((1 - ease(t / .9)) * 330)
            draw_char(canvas, t, mouth, slide)

            rgb = canvas.convert("RGB")
            d2 = ImageDraw.Draw(rgb)
            pbar(d2, t / total)
            if poster is None and t > 1.2:
                poster = rgb.copy()
            proc.stdin.write(rgb.tobytes())
            if f % 200 == 0:
                print("  %d/%d" % (f, nframes))
    finally:
        try:
            proc.stdin.close()
        except Exception:
            pass
        err = proc.stderr.read().decode("utf-8", "ignore") if proc.stderr else ""
        proc.wait(timeout=120)
        if err.strip():
            print("ffmpeg:", err.strip()[-400:])

    if poster is not None:
        poster.save(OUT_POSTER, quality=82)
    size = os.path.getsize(OUT_MP4) if os.path.exists(OUT_MP4) else 0
    print("产出：%s（%.1f MB）" % (OUT_MP4, size / 1048576.0))
    return 0 if proc.returncode == 0 and size > 0 else 1


def check():
    ok = os.path.exists(OUT_MP4) and os.path.getsize(OUT_MP4) > 100000
    print(("存在" if ok else "缺失") + " " + OUT_MP4)
    if ok:
        print("大小 %.1f MB" % (os.path.getsize(OUT_MP4) / 1048576.0))
    pok = os.path.exists(OUT_POSTER)
    print(("存在" if pok else "缺失") + " " + OUT_POSTER)
    return 0 if ok and pok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    return check() if a.check else render()


if __name__ == "__main__":
    sys.exit(main())
